#!/usr/bin/env python3
"""
Perth Container Litter Density & Containers for Change Cash Collection Map
Shows high-litter areas and official cash-for-containers collection points
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class PerthContainerLitterMap:
    def __init__(self):
        """Initialize the map with Perth coordinates."""
        self.perth_center = (-31.9505, 115.8605)
        
        # Containers for Change CASH collection points (official refund locations)
        self.cash_collection_points = [
            # Drive-Through Depots (10¢ per container)
            {'name': 'Return-It Balcatta Drive-Thru', 'coords': (-31.8700, 115.8300), 'type': 'drive_thru', 
             'address': 'Balcatta', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Cockburn Drive-Thru', 'coords': (-32.1200, 115.8500), 'type': 'drive_thru', 
             'address': 'Cockburn', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Shenton Park Drive-Thru', 'coords': (-31.9600, 115.8100), 'type': 'drive_thru', 
             'address': 'Shenton Park', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Welshpool Drive-Thru', 'coords': (-31.9900, 115.9300), 'type': 'drive_thru', 
             'address': 'Welshpool', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            
            # Automated Depots (24/7 access)
            {'name': 'Return-It Malaga Automated', 'coords': (-31.8600, 115.8900), 'type': 'automated', 
             'address': 'Malaga', 'refund_rate': '10¢ per container', 'hours': '24/7 access'},
            {'name': 'Return-It Butler/Clarkson Automated', 'coords': (-31.7200, 115.7000), 'type': 'automated', 
             'address': 'Butler/Clarkson', 'refund_rate': '10¢ per container', 'hours': '24/7 access'},
            {'name': 'Return-It Bunbury Automated', 'coords': (-33.3267, 115.6347), 'type': 'automated', 
             'address': 'Bunbury', 'refund_rate': '10¢ per container', 'hours': '24/7 access'},
            {'name': 'Return-It Geraldton Automated', 'coords': (-28.7774, 114.6147), 'type': 'automated', 
             'address': 'Geraldton', 'refund_rate': '10¢ per container', 'hours': '24/7 access'},
            
            # Scout Recycling Depots (community fundraising)
            {'name': 'Scouts Recycling Malaga', 'coords': (-31.8600, 115.8900), 'type': 'depot', 
             'address': 'Malaga', 'refund_rate': '10¢ per container', 'hours': 'Check local hours'},
            {'name': 'Scouts Recycling Wangara', 'coords': (-31.7800, 115.8300), 'type': 'depot', 
             'address': 'Wangara', 'refund_rate': '10¢ per container', 'hours': 'Check local hours'},
            {'name': 'Scouts Recycling Kenwick', 'coords': (-32.0300, 115.9600), 'type': 'depot', 
             'address': 'Kenwick', 'refund_rate': '10¢ per container', 'hours': 'Check local hours'},
            {'name': 'Scouts Recycling Cockburn', 'coords': (-32.1200, 115.8500), 'type': 'depot', 
             'address': 'Cockburn', 'refund_rate': '10¢ per container', 'hours': 'Check local hours'},
            
            # Reverse Vending Machines (instant cash/vouchers)
            {'name': 'Westfield Carousel RVM', 'coords': (-32.0177, 115.9344), 'type': 'rvm', 
             'address': 'Westfield Carousel', 'refund_rate': '10¢ per container', 'hours': 'Mall hours'},
            {'name': 'Garden City Shopping Centre RVM', 'coords': (-32.0600, 115.8000), 'type': 'rvm', 
             'address': 'Garden City', 'refund_rate': '10¢ per container', 'hours': 'Mall hours'},
            {'name': 'Westfield Innaloo RVM', 'coords': (-31.8950, 115.8050), 'type': 'rvm', 
             'address': 'Westfield Innaloo', 'refund_rate': '10¢ per container', 'hours': 'Mall hours'},
            {'name': 'Lakeside Joondalup RVM', 'coords': (-31.7448, 115.7661), 'type': 'rvm', 
             'address': 'Lakeside Joondalup', 'refund_rate': '10¢ per container', 'hours': 'Mall hours'},
        ]
        
        # High container litter density areas (where cans/bottles accumulate)
        self.litter_hotspots = [
            # Beaches (high tourist traffic, picnics, parties)
            {'name': 'Cottesloe Beach', 'coords': (-31.9959, 115.7581), 'type': 'beach', 'litter_density': 10, 
             'peak_times': 'Weekends, summer evenings', 'container_types': 'Beer cans, soft drink bottles, water bottles'},
            {'name': 'Scarborough Beach', 'coords': (-31.8944, 115.7581), 'type': 'beach', 'litter_density': 9, 
             'peak_times': 'Daily, especially weekends', 'container_types': 'Mixed beverage containers, energy drinks'},
            {'name': 'City Beach', 'coords': (-31.9400, 115.7600), 'type': 'beach', 'litter_density': 8, 
             'peak_times': 'Weekend afternoons', 'container_types': 'Beer bottles, soft drinks'},
            {'name': 'Hillarys Beach & Marina', 'coords': (-31.8194, 115.7372), 'type': 'beach', 'litter_density': 8, 
             'peak_times': 'Daily tourist traffic', 'container_types': 'Restaurant/cafe containers, tourist drinks'},
            {'name': 'Fremantle Beach', 'coords': (-32.0555, 115.7482), 'type': 'beach', 'litter_density': 9, 
             'peak_times': 'Market days, weekends', 'container_types': 'Tourist containers, market drinks'},
            {'name': 'Rockingham Beach', 'coords': (-32.2769, 115.7297), 'type': 'beach', 'litter_density': 7, 
             'peak_times': 'Family weekends, school holidays', 'container_types': 'Family drink containers, juice boxes'},
            
            # Parks & Recreation Areas
            {'name': 'Kings Park', 'coords': (-31.9590, 115.8331), 'type': 'park', 'litter_density': 9, 
             'peak_times': 'Events, festivals, weekends', 'container_types': 'Event containers, picnic drinks'},
            {'name': 'Whiteman Park', 'coords': (-31.8200, 115.9100), 'type': 'park', 'litter_density': 7, 
             'peak_times': 'Weekends, school holidays', 'container_types': 'Family containers, sports drinks'},
            {'name': 'Hyde Park', 'coords': (-31.9450, 115.8550), 'type': 'park', 'litter_density': 8, 
             'peak_times': 'Festivals, weekend events', 'container_types': 'Event beverages, food court drinks'},
            
            # Sports Venues (after events - goldmine for containers)
            {'name': 'Optus Stadium Surrounds', 'coords': (-31.9513, 115.8908), 'type': 'sports', 'litter_density': 10, 
             'peak_times': 'Post-game (AFL, cricket, concerts)', 'container_types': 'Beer cans, soft drinks, water bottles'},
            {'name': 'Perth Arena Area', 'coords': (-31.9481, 115.8614), 'type': 'sports', 'litter_density': 9, 
             'peak_times': 'Post-event evenings', 'container_types': 'Entertainment event containers'},
            {'name': 'HBF Park Surrounds', 'coords': (-31.9200, 115.8850), 'type': 'sports', 'litter_density': 8, 
             'peak_times': 'Post-match weekends', 'container_types': 'Sports drinks, beer cans'},
            {'name': 'WACA Ground Area', 'coords': (-31.9590, 115.8745), 'type': 'sports', 'litter_density': 8, 
             'peak_times': 'Cricket match days', 'container_types': 'Beer cans, soft drinks'},
            
            # Entertainment Districts (nightlife litter)
            {'name': 'Northbridge Streets', 'coords': (-31.9477, 115.8537), 'type': 'entertainment', 'litter_density': 10, 
             'peak_times': 'Weekend nights, early mornings', 'container_types': 'Beer bottles, energy drinks, pre-drinks'},
            {'name': 'Fremantle Entertainment District', 'coords': (-32.0555, 115.7482), 'type': 'entertainment', 'litter_density': 8, 
             'peak_times': 'Weekend evenings', 'container_types': 'Craft beer bottles, tourist drinks'},
            {'name': 'Leederville Precinct', 'coords': (-31.9356, 115.8413), 'type': 'entertainment', 'litter_density': 7, 
             'peak_times': 'Friday/Saturday nights', 'container_types': 'Restaurant drinks, bar containers'},
            {'name': 'Subiaco Entertainment Area', 'coords': (-31.9474, 115.8219), 'type': 'entertainment', 'litter_density': 7, 
             'peak_times': 'Weekend dining/nightlife', 'container_types': 'Wine bottles, craft beer cans'},
            
            # University Areas (student consumption)
            {'name': 'UWA Campus & Surrounds', 'coords': (-31.9806, 115.8178), 'type': 'education', 'litter_density': 9, 
             'peak_times': 'Semester periods, parties', 'container_types': 'Student drinks, party containers, energy drinks'},
            {'name': 'Curtin University Area', 'coords': (-32.0023, 115.8957), 'type': 'education', 'litter_density': 9, 
             'peak_times': 'Academic year, student events', 'container_types': 'Student beverages, sports drinks'},
            {'name': 'Murdoch University Surrounds', 'coords': (-32.0677, 115.8362), 'type': 'education', 'litter_density': 8, 
             'peak_times': 'Student events, orientation', 'container_types': 'Campus drinks, student party containers'},
            {'name': 'ECU Joondalup Campus', 'coords': (-31.7448, 115.7661), 'type': 'education', 'litter_density': 7, 
             'peak_times': 'Semester periods', 'container_types': 'Student beverages, energy drinks'},
            
            # Shopping Center Perimeters (food court overflow)
            {'name': 'Westfield Carousel Surrounds', 'coords': (-32.0177, 115.9344), 'type': 'shopping', 'litter_density': 8, 
             'peak_times': 'Daily shopping traffic', 'container_types': 'Food court drinks, takeaway containers'},
            {'name': 'Garden City Perimeter', 'coords': (-32.0600, 115.8000), 'type': 'shopping', 'litter_density': 8, 
             'peak_times': 'Weekend shopping', 'container_types': 'Shopping beverages, food court overflow'},
            {'name': 'Westfield Innaloo Area', 'coords': (-31.8950, 115.8050), 'type': 'shopping', 'litter_density': 7, 
             'peak_times': 'Cinema nights, weekends', 'container_types': 'Cinema drinks, food court containers'},
            {'name': 'Lakeside Joondalup Surrounds', 'coords': (-31.7448, 115.7661), 'type': 'shopping', 'litter_density': 7, 
             'peak_times': 'Weekend family shopping', 'container_types': 'Family drinks, food court beverages'},
            
            # Transport Hubs (traveler containers)
            {'name': 'Perth Airport Surrounds', 'coords': (-31.9403, 115.9669), 'type': 'transport', 'litter_density': 8, 
             'peak_times': 'Peak travel times', 'container_types': 'Travel beverages, duty-free containers'},
            {'name': 'Perth Train Station Area', 'coords': (-31.9505, 115.8605), 'type': 'transport', 'litter_density': 7, 
             'peak_times': 'Rush hours, weekends', 'container_types': 'Commuter drinks, coffee cups with deposit'},
            {'name': 'Elizabeth Quay Bus Area', 'coords': (-31.9565, 115.8614), 'type': 'transport', 'litter_density': 6, 
             'peak_times': 'Peak commuter times', 'container_types': 'Commuter beverages'},
            
            # Event & Festival Venues (post-event goldmines)
            {'name': 'Perth Convention Centre Area', 'coords': (-31.9565, 115.8614), 'type': 'events', 'litter_density': 8, 
             'peak_times': 'Post-conference/exhibition', 'container_types': 'Conference beverages, networking drinks'},
            {'name': 'Crown Perth Complex', 'coords': (-31.9731, 115.8781), 'type': 'events', 'litter_density': 9, 
             'peak_times': '24/7, peak weekends', 'container_types': 'Casino drinks, entertainment containers'},
            {'name': 'Claremont Showground', 'coords': (-31.9850, 115.7800), 'type': 'events', 'litter_density': 9, 
             'peak_times': 'Show days, market weekends', 'container_types': 'Fair drinks, market beverages'},
            
            # Markets & Festival Areas (high turnover)
            {'name': 'Fremantle Markets Area', 'coords': (-32.0555, 115.7482), 'type': 'markets', 'litter_density': 9, 
             'peak_times': 'Weekend market days', 'container_types': 'Market beverages, tourist drinks, food vendor containers'},
            {'name': 'Subiaco Farmers Market', 'coords': (-31.9474, 115.8219), 'type': 'markets', 'litter_density': 7, 
             'peak_times': 'Saturday mornings', 'container_types': 'Coffee containers, fresh juice bottles'},
            {'name': 'Kalamunda Markets', 'coords': (-31.9750, 116.0550), 'type': 'markets', 'litter_density': 6, 
             'peak_times': 'Weekend market days', 'container_types': 'Local beverage containers'},
            
            # Residential Hotspots (bin day collections)
            {'name': 'Claremont Residential', 'coords': (-31.9850, 115.7800), 'type': 'residential', 'litter_density': 6, 
             'peak_times': 'Bin collection days', 'container_types': 'Household beverage containers'},
            {'name': 'South Yarra Residential', 'coords': (-31.9200, 115.8400), 'type': 'residential', 'litter_density': 6, 
             'peak_times': 'Bin collection days', 'container_types': 'Residential drinks, wine bottles'},
        ]
        
    def create_map(self):
        """Create the comprehensive container litter and cash collection map."""
        # Initialize map centered on Perth
        m = folium.Map(
            location=self.perth_center,
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add different tile layers
        folium.TileLayer('CartoDB positron').add_to(m)
        folium.TileLayer('CartoDB dark_matter').add_to(m)
        
        # Create marker clusters
        cash_cluster = MarkerCluster(name='💰 Cash Collection Points (10¢ per container)').add_to(m)
        litter_cluster = MarkerCluster(name='🗑️ High Litter Density Areas').add_to(m)
        
        # Add cash collection points with detailed info
        for point in self.cash_collection_points:
            icon_color = {
                'drive_thru': 'green',      # Drive-through depots
                'automated': 'darkgreen',   # 24/7 automated
                'depot': 'orange',          # Scout depots
                'rvm': 'blue'              # Reverse vending machines
            }.get(point['type'], 'gray')
            
            icon_symbol = {
                'drive_thru': 'car',
                'automated': 'cog',
                'depot': 'home',
                'rvm': 'laptop'
            }.get(point['type'], 'recycle')
            
            folium.Marker(
                location=point['coords'],
                popup=f"""
                <div style="width: 250px;">
                <h4>💰 {point['name']}</h4>
                <b>🕒 Hours:</b> {point['hours']}<br>
                <b>💵 Rate:</b> {point['refund_rate']}<br>
                <b>📍 Location:</b> {point['address']}<br>
                <b>🏷️ Type:</b> {point['type'].replace('_', ' ').title()}<br>
                <br>
                <i>Official Containers for Change collection point</i><br>
                <i>Bring eligible containers for instant cash refund!</i>
                </div>
                """,
                tooltip=f"💰 {point['name']} - {point['refund_rate']}",
                icon=folium.Icon(color=icon_color, icon=icon_symbol, prefix='fa')
            ).add_to(cash_cluster)
        
        # Add litter hotspots with density info
        for area in self.litter_hotspots:
            icon_color = {
                'beach': 'lightblue',
                'park': 'lightgreen', 
                'sports': 'red',
                'entertainment': 'purple',
                'education': 'orange',
                'shopping': 'pink',
                'transport': 'gray',
                'events': 'darkred',
                'markets': 'cadetblue',
                'residential': 'beige'
            }.get(area['type'], 'gray')
            
            # Size marker based on litter density
            radius = area['litter_density'] * 2
            
            folium.CircleMarker(
                location=area['coords'],
                popup=f"""
                <div style="width: 280px;">
                <h4>🗑️ {area['name']}</h4>
                <b>📊 Litter Density:</b> {area['litter_density']}/10<br>
                <b>⏰ Peak Times:</b> {area['peak_times']}<br>
                <b>🥤 Container Types:</b> {area['container_types']}<br>
                <b>🏷️ Area Type:</b> {area['type'].title()}<br>
                <br>
                <i>High container litter accumulation area</i><br>
                <i>Check public bins and surrounding areas</i>
                </div>
                """,
                tooltip=f"🗑️ {area['name']} - Density: {area['litter_density']}/10",
                radius=radius,
                color='red',
                fill=True,
                fillColor=icon_color,
                fillOpacity=0.6,
                weight=2
            ).add_to(litter_cluster)
        
        # Create heatmap for litter density
        heat_data = [[area['coords'][0], area['coords'][1], area['litter_density']] 
                     for area in self.litter_hotspots]
        
        HeatMap(
            heat_data,
            name='🌡️ Container Litter Density Heatmap',
            radius=25,
            max_zoom=18,
            gradient={0.2: 'yellow', 0.4: 'orange', 0.6: 'red', 1: 'darkred'}
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add comprehensive legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 350px; height: 320px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:12px; padding: 15px; overflow-y: auto;">
        <h3>🗂️ Container Collection Guide</h3>
        
        <h4>💰 Cash Collection Points (10¢ each):</h4>
        <p><i class="fa fa-car" style="color:green"></i> <b>Drive-Thru Depots</b> - Quick service</p>
        <p><i class="fa fa-cog" style="color:darkgreen"></i> <b>Automated Depots</b> - 24/7 access</p>
        <p><i class="fa fa-home" style="color:orange"></i> <b>Scout Depots</b> - Community support</p>
        <p><i class="fa fa-laptop" style="color:blue"></i> <b>Reverse Vending</b> - Shopping centers</p>
        
        <h4>🗑️ Litter Density Areas:</h4>
        <p>🔴 <b>Size = Density</b> (bigger = more containers)</p>
        <p>🌡️ <b>Heatmap</b> shows concentration zones</p>
        
        <h4>📋 Collection Tips:</h4>
        <ul style="margin-top:5px;">
            <li><b>Best Times:</b> Post-events, weekend mornings</li>
            <li><b>High Value:</b> Sports venues, beaches, nightlife areas</li>
            <li><b>Eligible:</b> Cans, bottles with refund mark</li>
            <li><b>Legal:</b> Public bins, litter pickup only</li>
        </ul>
        
        <p><small><i>Always respect private property and local regulations</i></small></p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    def save_map(self, filename='perth_container_litter_cash_map.html'):
        """Save the map to an HTML file."""
        m = self.create_map()
        m.save(filename)
        print(f"Container litter and cash collection map saved as {filename}")
        return m
    
    def get_top_recommendations(self):
        """Get top container collection recommendations."""
        print("🏆 TOP CONTAINER COLLECTION HOTSPOTS:")
        print("=" * 50)
        
        # Sort by litter density
        sorted_areas = sorted(self.litter_hotspots, key=lambda x: x['litter_density'], reverse=True)
        
        for i, area in enumerate(sorted_areas[:15], 1):
            print(f"{i:2d}. {area['name']:<25} | Density: {area['litter_density']}/10 | {area['type'].title()}")
            print(f"    ⏰ {area['peak_times']}")
            print(f"    🥤 {area['container_types']}")
            print()
        
        print("\n💰 NEAREST CASH COLLECTION POINTS:")
        print("=" * 40)
        for point in self.cash_collection_points[:8]:
            print(f"💵 {point['name']} ({point['type'].replace('_', ' ').title()})")
            print(f"   📍 {point['address']} | 🕒 {point['hours']}")
            print()

# Create and display the map
if __name__ == "__main__":
    container_map = PerthContainerLitterMap()
    map_obj = container_map.create_map()
    
    # Display statistics
    print("🗺️  PERTH CONTAINER LITTER & CASH COLLECTION MAP")
    print("=" * 55)
    print(f"💰 Cash Collection Points: {len(container_map.cash_collection_points)}")
    print(f"🗑️  High Litter Density Areas: {len(container_map.litter_hotspots)}")
    print(f"💵 Potential Revenue: Up to ${len(container_map.litter_hotspots) * 50}/day")
    print()
    
    # Save the map
    container_map.save_map()
    
    # Show recommendations
    container_map.get_top_recommendations()