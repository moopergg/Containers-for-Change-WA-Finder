#!/usr/bin/env python3
"""
Perth Container Finder Chatbot - Terminal UI
Interactive chatbot to help find containers and litter hotspots in Perth, WA
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd
import warnings
import requests
import json
import os
import sys
from datetime import datetime
import re
from typing import Dict, List, Tuple
import time

warnings.filterwarnings('ignore')

class ContainerDataManager:
    """Manages all container collection and litter data for Perth"""
    
    def __init__(self):
        self.perth_center = (-31.9505, 115.8605)
        
        # Cash collection points
        self.cash_collection_points = [
            {'name': 'Return-It Balcatta Drive-Thru', 'coords': (-31.8700, 115.8300), 'type': 'drive_thru', 
             'address': 'Balcatta', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Cockburn Drive-Thru', 'coords': (-32.1200, 115.8500), 'type': 'drive_thru', 
             'address': 'Cockburn', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Shenton Park Drive-Thru', 'coords': (-31.9600, 115.8100), 'type': 'drive_thru', 
             'address': 'Shenton Park', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Welshpool Drive-Thru', 'coords': (-31.9900, 115.9300), 'type': 'drive_thru', 
             'address': 'Welshpool', 'refund_rate': '10¢ per container', 'hours': '7am-6pm daily'},
            {'name': 'Return-It Malaga Automated', 'coords': (-31.8600, 115.8900), 'type': 'automated', 
             'address': 'Malaga', 'refund_rate': '10¢ per container', 'hours': '24/7 access'},
            {'name': 'Return-It Butler/Clarkson Automated', 'coords': (-31.7200, 115.7000), 'type': 'automated', 
             'address': 'Butler/Clarkson', 'refund_rate': '10¢ per container', 'hours': '24/7 access'},
            {'name': 'Westfield Carousel RVM', 'coords': (-32.0177, 115.9344), 'type': 'rvm', 
             'address': 'Westfield Carousel', 'refund_rate': '10¢ per container', 'hours': 'Mall hours'},
            {'name': 'Garden City Shopping Centre RVM', 'coords': (-32.0600, 115.8000), 'type': 'rvm', 
             'address': 'Garden City', 'refund_rate': '10¢ per container', 'hours': 'Mall hours'},
        ]
        
        # Litter hotspots
        self.litter_hotspots = [
            {'name': 'Cottesloe Beach', 'coords': (-31.9959, 115.7581), 'type': 'beach', 'litter_density': 10, 
             'peak_times': 'Weekends, summer evenings', 'container_types': 'Beer cans, soft drink bottles, water bottles',
             'specific_areas': 'Main beach area near pavilion, north end near groyne, around beach volleyball courts'},
            {'name': 'Scarborough Beach', 'coords': (-31.8944, 115.7581), 'type': 'beach', 'litter_density': 9, 
             'peak_times': 'Daily, especially weekends', 'container_types': 'Mixed beverage containers, energy drinks',
             'specific_areas': 'Amphitheatre area, beachfront promenade, around surf club'},
            {'name': 'Kings Park', 'coords': (-31.9590, 115.8331), 'type': 'park', 'litter_density': 9, 
             'peak_times': 'Events, festivals, weekends', 'container_types': 'Event containers, picnic drinks',
             'specific_areas': 'Synergy Parkland, around DNA Tower, State War Memorial area'},
            {'name': 'Optus Stadium Surrounds', 'coords': (-31.9513, 115.8908), 'type': 'sports', 'litter_density': 10, 
             'peak_times': 'Post-game (AFL, cricket, concerts)', 'container_types': 'Beer cans, soft drinks, water bottles',
             'specific_areas': 'Burswood Park, around train stations, walkways to stadium'},
            {'name': 'Northbridge Streets', 'coords': (-31.9477, 115.8537), 'type': 'entertainment', 'litter_density': 10, 
             'peak_times': 'Weekend nights, early mornings', 'container_types': 'Beer bottles, energy drinks, pre-drinks',
             'specific_areas': 'William Street, James Street, Lake Street, Cultural Centre area'},
            {'name': 'Fremantle Beach', 'coords': (-32.0555, 115.7482), 'type': 'beach', 'litter_density': 9, 
             'peak_times': 'Market days, weekends', 'container_types': 'Tourist containers, market drinks',
             'specific_areas': 'Bathers Beach, around fishing boat harbour, near markets'},
            {'name': 'UWA Campus & Surrounds', 'coords': (-31.9806, 115.8178), 'type': 'education', 'litter_density': 9, 
             'peak_times': 'Semester periods, parties', 'container_types': 'Student drinks, party containers, energy drinks',
             'specific_areas': 'Hackett Drive, around student accommodation, near tavern'},
            {'name': 'Curtin University Area', 'coords': (-32.0023, 115.8957), 'type': 'education', 'litter_density': 9, 
             'peak_times': 'Academic year, student events', 'container_types': 'Student beverages, sports drinks',
             'specific_areas': 'Around student housing, near tavern, campus green areas'},
        ]
        
        # Location aliases for better matching
        self.location_aliases = {
            'cottesloe': 'Cottesloe Beach',
            'cott': 'Cottesloe Beach',
            'scarborough': 'Scarborough Beach',
            'scarbs': 'Scarborough Beach',
            'kings park': 'Kings Park',
            'optus': 'Optus Stadium Surrounds',
            'optus stadium': 'Optus Stadium Surrounds',
            'northbridge': 'Northbridge Streets',
            'fremantle': 'Fremantle Beach',
            'freo': 'Fremantle Beach',
            'uwa': 'UWA Campus & Surrounds',
            'curtin': 'Curtin University Area',
        }
    
    def find_location(self, query: str) -> Dict:
        """Find a location from the query string"""
        query_lower = query.lower()
        
        # Check direct matches in aliases
        for alias, location_name in self.location_aliases.items():
            if alias in query_lower:
                for hotspot in self.litter_hotspots:
                    if hotspot['name'] == location_name:
                        return hotspot
        
        # Check partial matches in hotspot names
        for hotspot in self.litter_hotspots:
            if any(word in hotspot['name'].lower() for word in query_lower.split()):
                return hotspot
        
        return None
    
    def get_nearby_collection_points(self, location_coords: Tuple[float, float], limit: int = 3) -> List[Dict]:
        """Get nearby collection points sorted by distance"""
        import math
        
        def distance(coord1, coord2):
            return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)
        
        points_with_distance = []
        for point in self.cash_collection_points:
            dist = distance(location_coords, point['coords'])
            point_copy = point.copy()
            point_copy['distance'] = dist
            points_with_distance.append(point_copy)
        
        return sorted(points_with_distance, key=lambda x: x['distance'])[:limit]

class ContainerChatbot:
    """Main chatbot class with OpenRouter API integration"""
    
    def __init__(self):
        self.data_manager = ContainerDataManager()
        
        # API Configuration
        self.api_key = "ADD_KEY_HERE"
        self.model_name = "ADD_MODEL_HERE"
        self.api_url = "ADD_API_URL_HERE"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Enhanced system prompt
        self.system_prompt = """You are a helpful Container/Bottle Finder Assistant for Perth, Western Australia. 
        
        You help people find cans, bottles, and containers in high-pollution areas around Perth for the Containers for Change program (10¢ per container).
        
        KEY RESPONSIBILITIES:
        1. When asked about specific locations, provide detailed information about where to find containers
        2. Give specific areas within locations (e.g., "at Cottesloe Beach, check near the pavilion, north end near groyne")
        3. Mention peak times when containers are most abundant
        4. Suggest nearby collection points for cashing in containers
        5. Provide practical tips for container collection
        
        RESPONSE STYLE:
        - Be enthusiastic and helpful
        - Use emojis appropriately (🥤🗑️💰📍⏰)
        - Give specific, actionable advice
        - Keep responses concise but informative
        - Always mention the 10¢ refund value
        
        IMPORTANT: You have access to real location data. When someone asks about a specific place, provide detailed local knowledge. Remember to ONLY answer questions about containers and Containers for Change. For example, don't respond to math equations. But you can respond to Containers for Change related equations. e.g. "If I have 100 containers, how much money can I make cashing them in at an exchange point?"""
        
        self.message_history = [{"role": "system", "content": self.system_prompt}]
    
    def format_message(self, role: str, content: str) -> Dict:
        """Format message for API"""
        return {"role": role, "content": content}
    
    def get_location_context(self, user_input: str) -> str:
        """Get relevant location data based on user input"""
        location = self.data_manager.find_location(user_input)
        context = ""
        
        if location:
            context += f"\n📍 LOCATION FOUND: {location['name']}\n"
            context += f"Litter Density: {location['litter_density']}/10\n"
            context += f"Peak Times: {location['peak_times']}\n"
            context += f"Container Types: {location['container_types']}\n"
            
            if 'specific_areas' in location:
                context += f"Specific Areas: {location['specific_areas']}\n"
            
            # Add nearby collection points
            nearby_points = self.data_manager.get_nearby_collection_points(location['coords'])
            context += f"\n💰 NEARBY COLLECTION POINTS:\n"
            for i, point in enumerate(nearby_points, 1):
                context += f"{i}. {point['name']} ({point['type']}) - {point['hours']}\n"
        
        return context
    
    def call_api(self, message: str) -> str:
        """Make API call to OpenRouter"""
        try:
            # Add location context to the message
            location_context = self.get_location_context(message)
            
            if location_context:
                enhanced_message = f"{message}\n\n[LOCATION DATA:{location_context}]"
            else:
                enhanced_message = message
            
            self.message_history.append(self.format_message("user", enhanced_message))
            
            payload = {
                "model": self.model_name,
                "messages": self.message_history,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                assistant_reply = data['choices'][0]['message']['content']
                self.message_history.append(self.format_message("assistant", assistant_reply))
                return assistant_reply
            else:
                return f"❌ API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def print_typing_effect(self, text: str, delay: float = 0.03):
        """Print text with typing effect"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()  # New line at the end
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
╔══════════════════════════════════════════════════════════════════════════════════╗
║                    🥤 PERTH CONTAINER FINDER CHATBOT 🥤                         ║
║                                                                                  ║
║    Find cans, bottles & containers around Perth, WA! 💰 10¢ per container       ║
║                                                                                  ║
║  📍 Ask about specific locations: "Where can I find cans at Cottesloe Beach?"   ║
║  🗺️  Get area recommendations: "Best places for container collection"           ║
║  💰 Find collection points: "Where can I cash in containers?"                   ║
║  📊 Check litter hotspots: "Show me high-density areas"                         ║
║                                                                                  ║
║  Commands: 'map' = generate map | 'quit' = exit | 'help' = show commands         ║
╚══════════════════════════════════════════════════════════════════════════════════╝
        """
        print(welcome_text)
        
    def display_help(self):
        """Display help information"""
        help_text = """
🆘 CONTAINER FINDER HELP:

📍 LOCATION QUERIES:
  • "Where can I find cans at Cottesloe Beach?"
  • "Best spots for containers in Fremantle?"
  • "Northbridge container collection areas?"

🗺️  GENERAL QUERIES:
  • "Show me the best container hotspots"
  • "Where are the highest density areas?"
  • "Best times to collect containers?"

💰 COLLECTION POINTS:
  • "Where can I cash in my containers?"
  • "Nearest collection points to [location]?"
  • "24/7 collection points in Perth?"

🛠️  COMMANDS:
  • 'map' - Generate interactive HTML map
  • 'stats' - Show collection statistics
  • 'help' - Show this help message
  • 'quit' - Exit the chatbot

💡 TIPS:
  • Be specific about locations for better results
  • Ask about peak times for maximum efficiency
  • Mention nearby areas for broader search
        """
        print(help_text)
    
    def generate_map(self):
        """Generate and save the interactive map"""
        try:
            print("\n🗺️  Generating interactive map...")
            
            # Create map
            m = folium.Map(
                location=self.data_manager.perth_center,
                zoom_start=10,
                tiles='OpenStreetMap'
            )
            
            # Add collection points
            cash_cluster = MarkerCluster(name='💰 Cash Collection Points').add_to(m)
            for point in self.data_manager.cash_collection_points:
                folium.Marker(
                    location=point['coords'],
                    popup=f"💰 {point['name']}<br>🕒 {point['hours']}<br>💵 {point['refund_rate']}",
                    tooltip=point['name'],
                    icon=folium.Icon(color='green', icon='dollar', prefix='fa')
                ).add_to(cash_cluster)
            
            # Add litter hotspots
            litter_cluster = MarkerCluster(name='🗑️ Litter Hotspots').add_to(m)
            for area in self.data_manager.litter_hotspots:
                folium.CircleMarker(
                    location=area['coords'],
                    popup=f"🗑️ {area['name']}<br>📊 Density: {area['litter_density']}/10<br>⏰ {area['peak_times']}",
                    tooltip=f"{area['name']} - {area['litter_density']}/10",
                    radius=area['litter_density'] * 2,
                    color='red',
                    fill=True,
                    fillOpacity=0.6
                ).add_to(litter_cluster)
            
            folium.LayerControl().add_to(m)
            
            # Save map
            filename = f"perth_containers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            m.save(filename)
            print(f"✅ Map saved as: {filename}")
            print(f"💻 Open in browser to view interactive map!")
            
        except Exception as e:
            print(f"❌ Error generating map: {e}")
    
    def show_stats(self):
        """Display collection statistics"""
        stats_text = f"""
📊 PERTH CONTAINER COLLECTION STATISTICS:

💰 Collection Points: {len(self.data_manager.cash_collection_points)}
🗑️  Litter Hotspots: {len(self.data_manager.litter_hotspots)}
💵 Potential Daily Value: ${len(self.data_manager.litter_hotspots) * 30}+

🏆 TOP DENSITY AREAS:
"""
        print(stats_text)
        
        # Sort by density
        sorted_areas = sorted(self.data_manager.litter_hotspots, 
                            key=lambda x: x['litter_density'], reverse=True)
        
        for i, area in enumerate(sorted_areas[:5], 1):
            print(f"  {i}. {area['name']} - {area['litter_density']}/10 density")
    
    def run(self):
        """Main chatbot loop"""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🤖 You: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using Perth Container Finder! Happy collecting! 💰")
                    break
                
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                
                elif user_input.lower() == 'map':
                    self.generate_map()
                    continue
                
                elif user_input.lower() == 'stats':
                    self.show_stats()
                    continue
                
                elif not user_input:
                    print("💭 Please enter a question or command!")
                    continue
                
                # Show typing indicator
                print("\n🤖 Assistant: ", end="")
                sys.stdout.flush()
                
                # Get AI response
                response = self.call_api(user_input)
                
                # Display response with typing effect
                self.print_typing_effect(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Happy container collecting! 💰")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'help' for assistance.")

if __name__ == "__main__":
    chatbot = ContainerChatbot()
    chatbot.run()
