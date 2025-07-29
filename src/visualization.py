import os
import geopandas as gpd
import folium
from folium.plugins import MiniMap, MeasureControl
from .config import SERVICE_CATEGORIES

def generate_enhanced_map(self,boundary, green_gdf, transit_gdf, services_gdf, sample_gdf, city):
        print("🗺️ Generating advanced interactive map...")
        boundary = boundary.to_crs(epsg=4326)
        green_gdf, transit_gdf, services_gdf, sample_gdf = [gdf.to_crs(epsg=4326) for gdf in [green_gdf, transit_gdf, services_gdf, sample_gdf]]
        center_proj = boundary.to_crs("EPSG:32643").geometry.centroid.iloc[0]
        center = gpd.GeoSeries([center_proj], crs="EPSG:32643").to_crs(epsg=4326).geometry.iloc[0]
        m = folium.Map(location=[center.y, center.x], zoom_start=12, tiles="cartodbpositron")

        folium.GeoJson(boundary.geometry.iloc[0], style_function=lambda x: {"fillColor": "gray", "color": "black", "weight": 2, "fillOpacity": 0.1},
                       name="City Boundary").add_to(m)

        if not green_gdf.empty:
            folium.GeoJson(green_gdf, style_function=lambda x: {"fillColor": "green", "color": "green", "weight": 1, "fillOpacity": 0.4},
                           name="Green Spaces").add_to(m)

        if not transit_gdf.empty:
            fg_transit = folium.FeatureGroup(name="Transit Stops")
            for _, row in transit_gdf.iterrows():
                geom = row.geometry
                if geom and not geom.is_empty:
                    pt = geom if geom.geom_type == "Point" else geom.centroid
                    folium.CircleMarker(location=[pt.y, pt.x], radius=3, color="blue", fill=True, fill_opacity=0.7).add_to(fg_transit)
            fg_transit.add_to(m)

        for category, amenities in SERVICE_CATEGORIES.items():
            fg = folium.FeatureGroup(name=f"Services: {category}")
            for _, row in services_gdf.iterrows():
                if ("amenity" in row and row["amenity"] in amenities) or ("shop" in row and row["shop"] in amenities):
                    geom = row.geometry
                    if geom and not geom.is_empty:
                        pt = geom if geom.geom_type == "Point" else geom.centroid
                        icon, icon_color = "info-sign", "blue"
                        if category == "Education": icon, icon_color = "graduation-cap", "green"
                        elif category == "Healthcare": icon, icon_color = "plus-sign", "red"
                        elif category == "Food & Drink": icon, icon_color = "cutlery", "orange"
                        elif category == "Banking": icon, icon_color = "inr", "darkgreen"
                        elif category == "Retail": icon, icon_color = "shopping-cart", "purple"
                        folium.Marker(location=[pt.y, pt.x],
                                      icon=folium.Icon(icon=icon, prefix="fa", color=icon_color),
                                      tooltip=row["amenity"] if "amenity" in row else row["shop"]).add_to(fg)
            fg.add_to(m)

        fg_high, fg_med, fg_low = [folium.FeatureGroup(name=label) for label in ["High Livability (≥0.7)", "Medium Livability (0.4–0.7)", "Low Livability (<0.4)"]]
        for _, row in sample_gdf.iterrows():
            geom = row.geometry
            if geom and not geom.is_empty:
                pt, score = geom if geom.geom_type == "Point" else geom.centroid, row["livability_score"]
                layer, color = (fg_high, "green") if score >= 0.7 else (fg_med, "orange") if score >= 0.4 else (fg_low, "red")
                popup_html = f"<b>Score:</b> {score:.2f}<br>✅ Green: {row['green_access']}<br>🚌 Transit: {row['transit_access']}<br>🏢 Services: {row['services_access']}"
                folium.CircleMarker([pt.y, pt.x], radius=5, color=color, fill=True, fill_opacity=0.8, popup=popup_html).add_to(layer)
        for fg in [fg_high, fg_med, fg_low]: fg.add_to(m)

        MiniMap().add_to(m)
        MeasureControl(primary_length_unit='meters').add_to(m)
        folium.LayerControl().add_to(m)
        m.get_root().html.add_child(folium.Element('''
            <div style="position: fixed; top: 10px; left: 10px; width: 200px; background: white; z-index:9999; padding:10px; border-radius:5px;">
                <h4>🏙️ Livability Legend</h4>
                <p><i class="fa fa-circle" style="color:green"></i> High (≥0.7)</p>
                <p><i class="fa fa-circle" style="color:orange"></i> Medium (0.4–0.7)</p>
                <p><i class="fa fa-circle" style="color:red"></i> Low (&lt;0.4)</p>
            </div>'''))

        city_clean = city.replace(',', '').replace(' ', '_').lower()
        m.save(f"{self.config.output_dir}/maps/{city_clean}_advanced_map.html")
        print(f"✅ Advanced map saved for {city}")
