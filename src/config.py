@dataclass
class AnalysisConfig:
    cities: List[str]
    num_samples: int = 200
    buffer_distances: Dict[str, int] = None
    max_nearest: int = 5
    use_folium: bool = True
    output_dir: str = "outputs"
    use_network_analysis: bool = True

    def __post_init__(self):
        if self.buffer_distances is None:
            self.buffer_distances = {
                "green": 800,
                "transit": 500,
                "services": 800
            }

# ============================
# SERVICE CATEGORY & WEIGHTS
# ============================
Green= {"leisure": ["park", "garden", "recreation_ground"]}

transit_tags = {
            "highway": "bus_stop",
            "amenity": ["bus_station"],
            "railway": ["station", "halt", "tram_stop", "subway_entrance"],
            "public_transport": ["platform", "stop_position"]
        }

SERVICE_CATEGORIES = {
    "Education": ["school", "college", "university"],
    "Healthcare": ["hospital", "clinic", "pharmacy"],
    "Food & Drink": ["restaurant", "cafe"],
    "Banking": ["bank", "atm"],
    "Retail": ["supermarket", "market", "mall", "convenience"]
} 


SERVICE_WEIGHTS = {
    "Education": 1.0,
    "Healthcare": 1.5,
    "Food & Drink": 0.5,
    "Banking": 0.3,
    "Retail": 0.3
}
