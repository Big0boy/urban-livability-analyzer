import numpy as np
import pandas as pd
import geopandas as gpd
import osmnx as ox
import networkx as nx
from joblib import Parallel, delayed
from config import SERVICE_CATEGORIES, SERVICE_WEIGHTS
from analyzer import LivabilityAnalyzer


def calculate_metrics(self:LivabilityAnalyzer,boundary, green_gdf, transit_gdf, services_gdf, G):
        samples = self.sample_points_within(boundary, self.config.num_samples)
        print(f"📊 Total sample points: {len(samples)}")
        print("🚦 Using A* network distance" if self.config.use_network_analysis else "🧭 Using Euclidean distance fallback")

        green_nodes, green_tree, _ = self.snap_features_to_nodes(G, green_gdf)
        transit_nodes, transit_tree, _ = self.snap_features_to_nodes(G, transit_gdf)
        print(f"✅ Green features snapped: {len(green_nodes)}")
        print(f"✅ Transit features snapped: {len(transit_nodes)}")

        print("🔍 Precomputing service categories...")
        cat_snap = {}
        for category, amenities in SERVICE_CATEGORIES.items():
            cat_gdf = services_gdf[
                (services_gdf.get("amenity").isin(amenities)) | (services_gdf.get("shop").isin(amenities))
            ]
            print(f"➡️ Service category '{category}': {len(cat_gdf)} features")
            nodes, tree, _ = self.snap_features_to_nodes(G, cat_gdf)
            cat_snap[category] = (nodes, tree)

        green_scores = Parallel(n_jobs=-1)(
            delayed(self.calc_score_astar)(self.config.buffer_distances["green"], G, pt, green_nodes, green_tree)
            for pt in samples.geometry)
        transit_scores = Parallel(n_jobs=-1)(
            delayed(self.calc_score_astar)(self.config.buffer_distances["transit"], G, pt, transit_nodes, transit_tree)
            for pt in samples.geometry)

        service_scores = []
        total_weight = sum(SERVICE_WEIGHTS.values())
        for pt in samples.geometry:
            weighted = 0
            for category, (cat_nodes, cat_tree) in cat_snap.items():
                cat_score = self.calc_score_astar(self.config.buffer_distances["services"], G, pt, cat_nodes, cat_tree)
                weighted += cat_score * SERVICE_WEIGHTS[category]
            normalized = weighted / total_weight
            service_scores.append(normalized)

        samples["green_access"] = green_scores
        samples["transit_access"] = transit_scores
        samples["services_access"] = service_scores
        samples["livability_score"] = (samples["green_access"] + samples["transit_access"] + samples["services_access"]) / 3

        metrics = {
            "Green Access": np.mean(green_scores),
            "Transit Access": np.mean(transit_scores),
            "Services Access": np.mean(service_scores),
            "Overall Livability": samples["livability_score"].mean()
        }
        summary_stats = {
            "total_samples": len(samples),
            "method": "A*" if self.config.use_network_analysis else "Euclidean",
            "high_pct": (samples["livability_score"] >= 0.7).mean() * 100,
            "medium_pct": ((samples["livability_score"] >= 0.4) & (samples["livability_score"] < 0.7)).mean() * 100,
            "low_pct": (samples["livability_score"] < 0.4).mean() * 100
        }
        return {"samples": samples, "metrics": metrics, "summary_stats": summary_stats}
