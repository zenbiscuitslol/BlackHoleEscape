import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import math
import time
from collections import deque

class BlackHoleEscape:
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the BlackHoleEscape system with 42 API credentials
        """
        self.base_url = "https://api.intra.42.fr"
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.rate_limit_queue = deque()
        self.authenticate()
    
    def rate_limit_delay(self):
        """Implement rate limiting: 2 requests per second"""
        now = time.time()
        while self.rate_limit_queue and now - self.rate_limit_queue[0] > 1:
            self.rate_limit_queue.popleft()
        
        if len(self.rate_limit_queue) >= 2:
            sleep_time = 1 - (now - self.rate_limit_queue[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.rate_limit_queue.append(time.time())
    
    def authenticate(self):
        """Authenticate with the 42 API using client credentials"""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=30
            )
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            print("✅ Successfully authenticated with 42 API")
        except requests.exceptions.RequestException as e:
            print(f"❌ Authentication failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
    
    def make_api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated API request to 42 Intra with rate limiting"""
        self.rate_limit_delay()
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 429:
                print("⚠️ Rate limit hit, waiting 5 seconds...")
                time.sleep(5)
                return self.make_api_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed for {endpoint}: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
            return {}
    
    def get_all_paginated_data(self, endpoint: str, params: Dict = None) -> List[Dict]:
        """Get all data from paginated endpoints"""
        all_data = []
        page = 1
        page_size = 100
        
        while True:
            if params is None:
                params = {}
            
            params['page'] = page
            params['per_page'] = page_size
            
            print(f"📄 Fetching page {page} for {endpoint}...")
            
            data = self.make_api_request(endpoint, params)
            
            if not data or not isinstance(data, list):
                break
                
            if not data:
                break
                
            all_data.extend(data)
            
            if len(data) < page_size:
                break
                
            page += 1
            
            if page > 10:  # Reduced safety limit
                print("⚠️ Safety limit reached, stopping pagination")
                break
        
        print(f"✅ Retrieved {len(all_data)} items from {endpoint}")
        return all_data
    
    def get_user_info(self, login: str) -> Dict:
        """Get basic user information"""
        return self.make_api_request(f"/v2/users/{login}")
    
    def get_user_cursus_users(self, user_id: int) -> List[Dict]:
        """Get user's cursus information including black hole date"""
        return self.get_all_paginated_data(f"/v2/users/{user_id}/cursus_users")
    
    def get_cursus_projects(self, cursus_id: int) -> List[Dict]:
        """Get all projects for a specific cursus"""
        return self.get_all_paginated_data(f"/v2/cursus/{cursus_id}/projects")
    
    def get_user_projects(self, user_id: int) -> List[Dict]:
        """Get all projects completed by user"""
        params = {'filter[user_id]': user_id}
        return self.get_all_paginated_data("/v2/projects_users", params)
    
    def get_42_circle_structure(self) -> Dict:
        """
        Define 42 circle structure with required projects for each circle
        """
        return {
            1: {
                "name": "Circle 1 - Fundamentals",
                "required_projects": ["libft"],
                "description": "Master C programming basics",
                "min_projects": 1
            },
            2: {
                "name": "Circle 2 - Core Systems",
                "required_projects": ["get_next_line", "ft_printf", "born2beroot"],
                "description": "File I/O, formatted output, and system administration",
                "min_projects": 2  # Need 2 out of 3 to progress
            },
            3: {
                "name": "Circle 3 - Algorithms & Graphics",
                "required_projects": ["pipex", "minitalk", "push_swap", "fdf", "fract-ol", "so_long"],
                "description": "Processes, signals, sorting algorithms, and 2D graphics",
                "min_projects": 3  # Need 3 out of 6 to progress
            },
            4: {
                "name": "Circle 4 - Advanced Systems",
                "required_projects": ["minishell", "Philosophers"],
                "description": "Shell implementation and concurrent programming",
                "min_projects": 1  # Need 1 out of 2 to progress
            },
            5: {
                "name": "Circle 5 - C++ & 3D",
                "required_projects": ["cpp-module-00", "cpp-module-01", "cpp-module-02", "cpp-module-03", "cpp-module-04", "cub3d", "netpractice", "minirt"],
                "description": "C++ programming and 3D graphics",
                "min_projects": 4  # Need 4 out of 8 to progress
            },
            6: {
                "name": "Circle 6 - Web & Networks",
                "required_projects": ["ft_irc", "webserv", "inception", "cpp-module-05", "cpp-module-06", "cpp-module-07", "cpp-module-08", "cpp-module-09"],
                "description": "Network programming and web services",
                "min_projects": 3  # Need 3 out of 8 to progress
            },
            7: {
                "name": "Circle 7 - Specialization",
                "required_projects": ["ft_transcendence"],
                "description": "Full-stack web application",
                "min_projects": 1
            }
        }
    
    def calculate_blackhole_status(self, login: str) -> Dict:
        """
        Calculate accurate black hole status using proper API endpoints
        """
        print(f"🔍 Analyzing black hole status for {login}...")
        
        user_info = self.get_user_info(login)
        if not user_info:
            return {"error": "User not found"}
        
        print(f"✅ Found user: {user_info.get('displayname', login)}")
        
        user_id = user_info.get("id")
        if not user_id:
            return {"error": "Could not get user ID"}
        
        # Get user's cursus information (contains black hole date!)
        cursus_users = self.get_user_cursus_users(user_id)
        if not cursus_users:
            return {"error": "No cursus information found"}
        
        # Find the main 42 cursus (usually the first one)
        main_cursus = None
        for cursus in cursus_users:
            cursus_name = cursus.get('cursus', {}).get('name', '').lower()
            if '42' in cursus_name or cursus.get('cursus_id') == 1:
                main_cursus = cursus
                break
        
        if not main_cursus:
            main_cursus = cursus_users[0]  # Fallback to first cursus
        
        # Extract key information
        blackholed_at = main_cursus.get('blackholed_at')
        begin_at = main_cursus.get('begin_at')  # This is the start date
        level = main_cursus.get('level', 0)
        cursus_id = main_cursus.get('cursus_id')
        cursus_name = main_cursus.get('cursus', {}).get('name', 'Unknown Cursus')
        
        # Get user's projects
        user_projects = self.get_user_projects(user_id)
        
        # Calculate current status with safe date handling
        current_date = datetime.now().astimezone()
        
        # FIXED: Calculate black hole date properly
        blackhole_date, days_until_blackhole, is_blackholed = self._calculate_blackhole_date(
            blackholed_at, begin_at, current_date
        )
        
        # Calculate projects information
        completed_projects = self._get_completed_projects(user_projects)
        
        # Calculate circle progress using the new accurate method
        circle_info = self._calculate_circle_progress(completed_projects)
        
        # Get the actual remaining projects for the CURRENT circle
        current_circle_projects = self._get_remaining_projects_for_current_circle(
            completed_projects, 
            circle_info.get('current_circle', 0)
        )
        
        # Calculate risk level safely
        risk_level = self._calculate_risk_level(days_until_blackhole, level, circle_info)
        
        return {
            "user_login": user_info.get("login"),
            "user_name": user_info.get("displayname"),
            "cursus": cursus_name,
            "level": level,
            "begin_at": begin_at,
            "blackholed_at": blackholed_at,
            "blackhole_date": blackhole_date.isoformat() if blackhole_date else None,
            "days_until_blackhole": days_until_blackhole,
            "is_blackholed": is_blackholed,
            "total_completed": len(completed_projects),
            "circle_info": circle_info,
            "remaining_projects": current_circle_projects,
            "risk_level": risk_level
        }
    
    def _calculate_blackhole_date(self, blackholed_at: str, begin_at: str, current_date: datetime) -> Tuple[Optional[datetime], Optional[int], bool]:
        """
        Calculate black hole date accurately based on 42 rules
        """
        # If API provides blackholed_at, use it directly
        if blackholed_at:
            try:
                blackhole_date = datetime.fromisoformat(blackholed_at.replace('Z', '+00:00'))
                days_until = (blackhole_date - current_date).days
                is_blackholed = days_until <= 0
                return blackhole_date, days_until, is_blackholed
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error parsing API blackhole date: {e}")
        
        # If no blackholed_at from API, calculate based on 42 rules
        if begin_at:
            try:
                start_date = datetime.fromisoformat(begin_at.replace('Z', '+00:00'))
                
                # 42 standard black hole period: 392 days (56 weeks) from start date
                blackhole_period_days = 392
                calculated_blackhole_date = start_date + timedelta(days=blackhole_period_days)
                
                days_until = (calculated_blackhole_date - current_date).days
                is_blackholed = days_until <= 0
                
                print(f"📅 Calculated black hole date: {calculated_blackhole_date.date()} "
                      f"(392 days from start: {start_date.date()})")
                
                return calculated_blackhole_date, days_until, is_blackholed
                
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error calculating black hole date: {e}")
        
        # If we can't calculate, return None values
        return None, None, False
    
    def _get_completed_projects(self, projects_users: List[Dict]) -> List[Dict]:
        """Get completed and validated projects"""
        completed = []
        for project_user in projects_users:
            if not isinstance(project_user, dict):
                continue
                
            status = project_user.get("status", "")
            final_mark = project_user.get("final_mark", 0)
            
            # Safely check if project is completed
            if status in ["finished", "success"] and final_mark is not None and final_mark >= 50:
                project_data = project_user.get("project", {})
                if project_data:
                    completed.append({
                        "id": project_data.get("id"),
                        "name": project_data.get("name"),
                        "slug": project_data.get("slug"),
                        "final_mark": final_mark,
                    })
        return completed
    
    def _calculate_circle_progress(self, completed_projects: List[Dict]) -> Dict:
        """
        Calculate current circle based on milestone projects
        FIXED: You are in a circle as soon as you start working on it, not when you complete all projects
        """
        def _normalize_name(name: str) -> str:
            """Normalize project name for comparison"""
            if not name:
                return ""
            name = name.lower().strip()
            # Remove common variations
            name = name.replace('_', ' ').replace('-', ' ')
            # Remove extra spaces
            name = ' '.join(name.split())
            return name

        # Build set of completed project names (normalized)
        completed_names = {_normalize_name(p.get("name", "")) for p in completed_projects}
        completed_slugs = {_normalize_name(p.get("slug", "")) for p in completed_projects}
        all_completed = completed_names.union(completed_slugs)
        
        circle_structure = self.get_42_circle_structure()
        
        current_circle = 1  # Start at circle 1 (everyone is at least in circle 1 after piscine)
        highest_circle_with_progress = 1
        
        # Find the highest circle where the user has made progress
        for circle_num in sorted(circle_structure.keys()):
            circle_data = circle_structure[circle_num]
            required_projects = circle_data["required_projects"]
            min_projects = circle_data.get("min_projects", 1)
            
            # Count how many required projects for this circle are completed
            completed_count = 0
            for project in required_projects:
                normalized_project = _normalize_name(project)
                found = False
                
                # Check if this project (or variation) is completed
                for completed in all_completed:
                    if normalized_project in completed or completed in normalized_project:
                        found = True
                        break
                
                if found:
                    completed_count += 1
            
            # If user has completed at least 1 project in this circle, they've reached it
            if completed_count > 0:
                highest_circle_with_progress = circle_num
                
            # If user has completed minimum required projects, they can progress
            if completed_count >= min_projects:
                current_circle = circle_num + 1  # They can move to next circle
            else:
                # Stop at the first circle where they haven't met requirements
                break
        
        # Ensure current circle doesn't exceed the highest circle with progress
        current_circle = min(current_circle, highest_circle_with_progress + 1)
        current_circle = min(current_circle, max(circle_structure.keys()))
        
        # Calculate progress for current circle
        current_circle_data = circle_structure.get(current_circle, {})
        current_required = current_circle_data.get("required_projects", [])
        current_min = current_circle_data.get("min_projects", 1)
        
        completed_in_current = 0
        missing_in_current = []
        
        for project in current_required:
            normalized_project = _normalize_name(project)
            found = False
            
            for completed in all_completed:
                if normalized_project in completed or completed in normalized_project:
                    found = True
                    break
            
            if found:
                completed_in_current += 1
            else:
                missing_in_current.append(project)
        
        remaining_in_current = max(0, current_min - completed_in_current)
        is_on_track = completed_in_current >= current_min
        
        next_circle = current_circle + 1 if current_circle < max(circle_structure.keys()) else None
        
        return {
            "current_circle": current_circle,
            "next_circle": next_circle,
            "completed_in_current": completed_in_current,
            "required_in_current": current_min,
            "remaining_in_current": remaining_in_current,
            "missing_projects": missing_in_current,
            "is_on_track": is_on_track,
            "current_circle_name": circle_structure.get(current_circle, {}).get("name", f"Circle {current_circle}"),
            "next_circle_name": circle_structure.get(next_circle, {}).get("name", f"Circle {next_circle}") if next_circle else None,
            "highest_circle_reached": highest_circle_with_progress
        }
    
    def _get_remaining_projects_for_current_circle(self, completed_projects: List[Dict], current_circle: int) -> List[Dict]:
        """Get only the projects needed for the CURRENT circle progression"""
        if not current_circle:
            return []
        
        circle_structure = self.get_42_circle_structure()
        current_circle_data = circle_structure.get(current_circle, {})
        required_projects = current_circle_data.get("required_projects", [])
        
        def _normalize_name(name: str) -> str:
            if not name:
                return ""
            name = name.lower().strip()
            name = name.replace('_', ' ').replace('-', ' ')
            name = ' '.join(name.split())
            return name
        
        # Get completed project names
        completed_names = {_normalize_name(p.get("name", "")) for p in completed_projects}
        completed_slugs = {_normalize_name(p.get("slug", "")) for p in completed_projects}
        all_completed = completed_names.union(completed_slugs)
        
        # Find which required projects are NOT completed
        remaining = []
        for project in required_projects:
            normalized_project = _normalize_name(project)
            found = False
            
            # Check if this project is already completed
            for completed in all_completed:
                if normalized_project in completed or completed in normalized_project:
                    found = True
                    break
            
            if not found:
                remaining.append({
                    "name": project,
                    "slug": project.lower().replace(' ', '-'),
                    "description": f"Required for {current_circle_data.get('name', f'Circle {current_circle}')}",
                    "circle": current_circle
                })
        
        return remaining
    
    def _calculate_risk_level(self, days_until_blackhole: Optional[int], current_level: float, circle_info: Dict) -> str:
        """Calculate risk level based on black hole date and progress"""
        if days_until_blackhole is None:
            return "UNKNOWN"
        
        safe_days = days_until_blackhole
        safe_level = current_level if current_level is not None else 0
        current_circle = circle_info.get("current_circle", 0)
        is_on_track = circle_info.get("is_on_track", False)
        
        if safe_days <= 0:
            return "BLACK_HOLED"
        elif safe_days <= 30:
            return "CRITICAL"
        elif safe_days <= 60:
            return "HIGH"
        elif safe_days <= 90:
            return "MEDIUM"
        elif safe_days <= 180 and not is_on_track:
            return "LOW"
        elif safe_level < 3.0 and current_circle <= 2 and safe_days <= 270:
            return "LOW"  # New students in early circles have more time
        else:
            return "SAFE"
    
    def generate_escape_plan(self, login: str) -> Dict:
        """
        Generate a customized escape plan based on accurate black hole information
        """
        status = self.calculate_blackhole_status(login)
        
        if "error" in status:
            return status
        
        if status.get("is_blackholed"):
            return {
                "status": status,
                "escape_plan": {
                    "message": "🚨 EMERGENCY: You have been black holed!",
                    "recommendations": [
                        "🚨 Immediately contact your campus staff",
                        "📞 Speak with your assigned tutor or referent",
                        "💡 Discuss options for appeal or re-entry",
                        "📝 Prepare a detailed progress report",
                        "🎯 Create a recovery plan with staff guidance"
                    ]
                }
            }
        
        # Generate proactive escape plan
        days_remaining = status.get("days_until_blackhole")
        circle_info = status.get("circle_info", {})
        remaining_projects = status.get("remaining_projects", [])
        begin_at = status.get("begin_at")
        
        if days_remaining is None or days_remaining > 1000:
            return {
                "status": status,
                "escape_plan": {
                    "message": "✅ No black hole date set - you're safe for now!",
                    "recommendations": [
                        "🎯 Focus on consistent project completion",
                        "📈 Aim for at least 1 project per week",
                        "👥 Collaborate with peers on difficult projects",
                        "📚 Use available learning resources",
                        "⏰ Maintain steady progress to avoid future risks"
                    ]
                }
            }
        
        # Use the accurate projects needed for the CURRENT circle
        projects_needed = circle_info.get("remaining_in_current", 0)
        missing_projects = circle_info.get("missing_projects", [])
        
        # Ensure we have valid numbers for calculations
        safe_days_remaining = max(1, days_remaining) if days_remaining is not None else 30
        safe_projects_needed = max(1, projects_needed)
        
        weekly_pace = math.ceil(safe_projects_needed / max(1, safe_days_remaining / 7))
        daily_pace = safe_projects_needed / safe_days_remaining
        
        # Create weekly plan focusing only on the missing projects for current circle
        weekly_plan = self._create_weekly_schedule(remaining_projects, safe_days_remaining, safe_projects_needed)
        
        escape_plan = {
            "start_date": begin_at,
            "blackhole_date": status.get("blackhole_date"),
            "days_remaining": days_remaining,
            "current_circle": circle_info.get("current_circle", 0),
            "current_circle_name": circle_info.get("current_circle_name", ""),
            "next_circle": circle_info.get("next_circle"),
            "next_circle_name": circle_info.get("next_circle_name", ""),
            "projects_completed_current": circle_info.get("completed_in_current", 0),
            "projects_required_current": circle_info.get("required_in_current", 0),
            "projects_remaining_current": projects_needed,
            "required_projects": safe_projects_needed,
            "recommended_weekly_pace": weekly_pace,
            "recommended_daily_pace": f"{daily_pace:.2f} projects per day",
            "weekly_schedule": weekly_plan,
            "priority_projects": [p.get("name", "Unknown") for p in remaining_projects],
            "missing_projects": missing_projects,
            "recommendations": self._generate_recommendations(status, days_remaining, weekly_pace)
        }
        
        return {
            "status": status,
            "escape_plan": escape_plan
        }
    
    def _create_weekly_schedule(self, projects: List[Dict], days_remaining: int, required_count: int) -> List[Dict]:
        """Create a weekly study schedule focusing only on required projects"""
        if not projects:
            return []
            
        weeks = math.ceil(days_remaining / 7) if days_remaining else 4
        projects_per_week = math.ceil(required_count / max(1, weeks))
        
        weekly_schedule = []
        
        for week in range(1, weeks + 1):
            if not projects:
                break
                
            # Take projects for this week
            week_projects = projects[:projects_per_week]
            projects = projects[projects_per_week:]  # Remove taken projects
            
            weekly_schedule.append({
                "week": week,
                "target_projects": len(week_projects),
                "projects": [
                    {
                        "name": p.get("name", "Unknown Project"), 
                        "description": p.get("description", "Required project")
                    } for p in week_projects
                ],
                "weekly_goals": [
                    f"Complete {len(week_projects)} required projects",
                    f"Focus on: {', '.join([p.get('name', 'Unknown') for p in week_projects])}",
                    "Attend relevant workshops",
                    "Get peer code reviews",
                    "Schedule evaluations early"
                ]
            })
        
        return weekly_schedule
    
    def _generate_recommendations(self, status: Dict, days_remaining: Optional[int], weekly_pace: int) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        risk_level = status.get("risk_level", "UNKNOWN")
        current_level = status.get("level", 0)
        circle_info = status.get("circle_info", {})
        begin_at = status.get("begin_at")
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "🚨 CRITICAL: Maximum effort required!",
                "🎯 Focus exclusively on required projects for current circle",
                "⏰ Dedicate 6-8 hours daily to coding",
                "🆘 Seek immediate help from staff and peers",
                "📞 Schedule daily check-ins with your tutor"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ HIGH RISK: Significant effort needed",
                "🎯 Prioritize circle progression over everything",
                "⏰ Dedicate 4-6 hours daily to coding",
                "👥 Form study groups for accountability",
                "📊 Track progress daily"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "🔶 MEDIUM RISK: Stay consistent and focused",
                "🎯 Maintain steady project completion pace",
                "⏰ Dedicate 3-4 hours daily to coding",
                "👥 Regular peer programming sessions",
                "📈 Weekly progress reviews"
            ])
        else:
            recommendations.extend([
                "✅ You're on track! Maintain consistency",
                "🎯 Focus on quality project completion",
                "⏰ 2-3 hours of focused coding daily",
                "👥 Help peers and reinforce learning"
            ])
        
        # Add circle-specific advice
        current_circle = circle_info.get("current_circle", 0)
        completed_in_current = circle_info.get("completed_in_current", 0)
        required_in_current = circle_info.get("required_in_current", 0)
        
        recommendations.append(f"🎯 You are in Circle {current_circle}: {completed_in_current}/{required_in_current} projects completed")
        
        # Add black hole specific info
        if begin_at:
            try:
                start_date = datetime.fromisoformat(begin_at.replace('Z', '+00:00'))
                days_since_start = (datetime.now().astimezone() - start_date).days
                recommendations.append(f"📅 Started: {start_date.date()} ({days_since_start} days ago)")
            except:
                pass
        
        if current_circle <= 2:
            recommendations.extend([
                "🌱 Focus on mastering C fundamentals and memory management",
                "💡 Practice debugging with valgrind and gdb"
            ])
        elif current_circle <= 4:
            recommendations.extend([
                "🚀 Work on algorithm optimization and system design",
                "🔧 Learn multi-process and multi-threaded programming"
            ])
        else:
            recommendations.extend([
                "🌟 You're in advanced territory - focus on architecture",
                "💡 Consider specialization paths and career goals"
            ])
        
        return recommendations

def main():
    """
    Main function to demonstrate the accurate BlackHoleEscape system
    """
    CLIENT_ID = "u-s4t2ud-3f5a9f13d7684887260aa74bef6284a20f40ca1ebb45a79c84cca875bec5cb72"
    CLIENT_SECRET = "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"
    
    try:
        escape_system = BlackHoleEscape(CLIENT_ID, CLIENT_SECRET)
        
        # Test with a real 42 login
        student_login = input("Enter 42 login: ").strip()
        if not student_login:
            student_login = "kskender"  # Fallback for testing
        
        print(f"🚀 Starting Accurate Black Hole Escape Analysis for {student_login}...")
        print("=" * 70)
        
        result = escape_system.generate_escape_plan(student_login)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        status = result["status"]
        plan = result.get("escape_plan", {})
        
        print(f"\n📊 ACCURATE BLACK HOLE ANALYSIS")
        print(f"👤 Student: {status.get('user_name', status.get('user_login'))}")
        print(f"🎓 Cursus: {status.get('cursus', 'Unknown')}")
        print(f"📈 Level: {status.get('level', 'Unknown')}")
        print(f"🎯 Risk Level: {status.get('risk_level', 'UNKNOWN')}")
        
        blackhole_date = status.get('blackhole_date')
        begin_at = status.get('begin_at')
        
        if begin_at:
            try:
                start_date = datetime.fromisoformat(begin_at.replace('Z', '+00:00'))
                days_since_start = (datetime.now().astimezone() - start_date).days
                print(f"📅 Start Date: {start_date.date()} ({days_since_start} days ago)")
            except:
                pass
        
        if blackhole_date:
            print(f"⏰ Black Hole Date: {blackhole_date}")
            print(f"📆 Days Remaining: {status.get('days_until_blackhole', 'Unknown')}")
        else:
            print(f"⏰ Black Hole Date: Not set (safe for now)")
        
        print(f"✅ Projects Completed: {status.get('total_completed', 0)}")
        
        circle_info = status.get('circle_info', {})
        current_circle = circle_info.get('current_circle', 0)
        print(f"🔄 Current Circle: {current_circle} - {circle_info.get('current_circle_name', '')}")
        print(f"📊 Progress in Circle {current_circle}: {circle_info.get('completed_in_current', 0)}/{circle_info.get('required_in_current', 0)} projects")
        
        next_circle = circle_info.get('next_circle')
        if next_circle is not None:
            print(f"🎯 Next Circle: {next_circle} - {circle_info.get('next_circle_name', '')}")
        
        if plan:
            print(f"\n📝 PERSONALIZED ESCAPE PLAN")
            if 'message' in plan:
                print(plan['message'])
            else:
                print(f"🎯 Required Projects for Circle {plan.get('current_circle')}: {plan.get('projects_remaining_current', 0)}")
                print(f"📈 Recommended Pace: {plan.get('recommended_daily_pace', 'N/A')}")
                print(f"📅 Weekly Target: {plan.get('recommended_weekly_pace', 0)} projects/week")
                
                # Show exactly which projects are missing
                missing_projects = plan.get('missing_projects', [])
                if missing_projects:
                    print(f"\n🎯 SPECIFIC PROJECTS NEEDED FOR CIRCLE {plan.get('current_circle')}:")
                    for i, project in enumerate(missing_projects, 1):
                        print(f"  {i}. {project}")
                
                weekly_schedule = plan.get('weekly_schedule', [])
                if weekly_schedule:
                    print(f"\n📅 WEEKLY ACTION PLAN:")
                    for week in weekly_schedule:
                        print(f"\nWeek {week.get('week', '?')}: {week.get('target_projects', 0)} projects")
                        for project in week.get('projects', []):
                            print(f"   • {project.get('name', 'Unknown')}")
            
            priority_projects = plan.get('priority_projects', [])
            if priority_projects:
                print(f"\n🎯 PRIORITY PROJECTS (in order):")
                for i, project in enumerate(priority_projects, 1):
                    print(f"  {i}. {project}")
            
            recommendations = plan.get('recommendations', [])
            if recommendations:
                print(f"\n💡 EXPERT RECOMMENDATIONS:")
                for rec in recommendations:
                    print(f"  • {rec}")
            
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()