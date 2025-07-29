from config import AnalysisConfig, Green, transit_tags, SERVICE_CATEGORIES
import os
import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
from shapely.geometry import Point
from scipy.spatial import cKDTree
from metrics import calculate_metrics
from visualization import generate_enhanced_map


class LivabilityAnalyzer:
    def __init__(self, config: AnalysisConfig):
        self.config = config
        for subdir in ['maps', 'data', 'reports']:
            os.makedirs(os.path.join(self.config.output_dir, subdir), exist_ok=True)

    def load_city_data(self, city: str):
        print(f"🌍 Loading city: {city}")
        boundary = ox.geocode_to_gdf(city)
        target_crs = "EPSG:32643"
        boundary = boundary.to_crs(target_crs)
        polygon = boundary.to_crs(epsg=4326).unary_union  # fix: use unary_union, not union_all

        green_gdf = ox.features_from_place(city, Green).to_crs(target_crs)
        print(f"✅ Green spaces: {len(green_gdf)} features")

        transit_gdf = ox.features_from_place(city, transit_tags).to_crs(target_crs)
        print(f"✅ Transit stops: {len(transit_gdf)} features")

        amenities_gdf = ox.features_from_place(city, {"amenity": True}).to_crs(target_crs)
        shops_gdf = ox.features_from_place(city, {"shop": True}).to_crs(target_crs)
        services_gdf = pd.concat([amenities_gdf, shops_gdf], ignore_index=True).drop_duplicates()
        print(f"✅ Services (amenity+shop): {len(services_gdf)} features")

        G = None
        if self.config.use_network_analysis:
            G = ox.graph_from_polygon(polygon, network_type="walk")
            print(f"🗺️ Street network: {len(G.nodes)} nodes, {len(G.edges)} edges")

        return boundary, green_gdf, transit_gdf, services_gdf, G

    def sample_points_within(self, boundary, num_samples):
        print(f"🎯 Sampling {num_samples} points...")
        minx, miny, maxx, maxy = boundary.total_bounds
        points = []
        union_geom = boundary.unary_union
        while len(points) < num_samples:
            x = np.random.uniform(minx, maxx)
            y = np.random.uniform(miny, maxy)
            pt = Point(x, y)
            if union_geom.contains(pt):
                points.append(pt)
        return gpd.GeoDataFrame(geometry=points, crs=boundary.crs)

    def snap_features_to_nodes(self, G, gdf):
        nodes, xy = [], []
        for geom in gdf.geometry:
            if geom.is_empty or not geom.is_valid:
                continue
            pt = geom.centroid if geom.geom_type != "Point" else geom
            x, y = pt.x, pt.y
            try:
                node = ox.distance.nearest_nodes(G, x, y)
                nodes.append(node)
                xy.append((x, y))
            except:
                continue
        tree = cKDTree(xy) if xy else None
        return nodes, tree, xy

    def calc_score_astar(self, buffer_dist, G, sample_point, feature_nodes, tree):
        if not feature_nodes or not tree or G is None:
            return 0.0
        try:
            orig_node = ox.distance.nearest_nodes(G, sample_point.x, sample_point.y)
        except:
            return 0.0
        _, idxs = tree.query([sample_point.x, sample_point.y], k=min(self.config.max_nearest, len(feature_nodes)))
        min_dist = float("inf")
        for i in np.atleast_1d(idxs):
            dest_node = feature_nodes[i]
            try:
                path_length = nx.astar_path_length(
                    G, orig_node, dest_node,
                    heuristic=lambda u, v: ox.distance.euclidean_dist_vec(
                        G.nodes[u]['y'], G.nodes[u]['x'],
                        G.nodes[v]['y'], G.nodes[v]['x']
                    ), weight="length")
                if path_length < min_dist:
                    min_dist = path_length
            except:
                continue
        return 1.0 if min_dist <= buffer_dist else 0.0
    def save_results(self, samples, city):
        city_clean = city.replace(',', '').replace(' ', '_').lower()
        samples.to_file(f"{self.config.output_dir}/data/{city_clean}_samples.geojson", driver="GeoJSON")
        samples.drop(columns='geometry').to_csv(f"{self.config.output_dir}/data/{city_clean}_samples.csv", index=False)
        print(f"✅ Results saved for {city}")

    def generate_comprehensive_report(self, results, city):
        print("\n📊 Summary Report")
        for k, v in results["metrics"].items():
            print(f"{k}: {v:.3f}")
        for k, v in results["summary_stats"].items():
            if isinstance(v, (float, int)):
                print(f"{k}: {v:.2f}")
            else:
                print(f"{k}: {v}")
        city_clean = city.replace(',', '').replace(' ', '_').lower()
        pd.DataFrame([results["summary_stats"]]).to_csv(f"{self.config.output_dir}/reports/{city_clean}_summary.csv", index=False)
        print(f"✅ Summary CSV saved for {city}")
    def run(self):
        for city in self.config.cities:
            boundary, green, transit, services, G = self.load_city_data(city)
            results = calculate_metrics(self,boundary, green, transit, services, G)
            self.generate_comprehensive_report(results, city)
            self.save_results(results["samples"], city)
            if self.config.use_folium:
                generate_enhanced_map(self,boundary, green, transit, services, results["samples"], city)
