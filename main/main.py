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
    
    def get_project_time_estimates(self) -> Dict:
        """
        Get realistic time estimates for 42 projects based on actual curriculum
        and student feedback
        """
        return {
            # Circle 1
            "libft": {"weeks": 2, "difficulty": "medium", "hours": 40, "type": "foundation"},
            
            # Circle 2
            "get_next_line": {"weeks": 1, "difficulty": "medium", "hours": 25, "type": "file_io"},
            "ft_printf": {"weeks": 2, "difficulty": "hard", "hours": 50, "type": "formatting"},
            "born2beroot": {"weeks": 1, "difficulty": "easy", "hours": 20, "type": "sysadmin"},
            
            # Circle 3
            "pipex": {"weeks": 2, "difficulty": "hard", "hours": 45, "type": "processes"},
            "minitalk": {"weeks": 1, "difficulty": "medium", "hours": 30, "type": "signals"},
            "push_swap": {"weeks": 3, "difficulty": "very_hard", "hours": 80, "type": "algorithms"},
            "fdf": {"weeks": 2, "difficulty": "medium", "hours": 40, "type": "graphics"},
            "fract-ol": {"weeks": 2, "difficulty": "medium", "hours": 35, "type": "graphics"},
            "so_long": {"weeks": 2, "difficulty": "medium", "hours": 40, "type": "game"},
            
            # Circle 4
            "minishell": {"weeks": 4, "difficulty": "very_hard", "hours": 120, "type": "systems"},
            "Philosophers": {"weeks": 3, "difficulty": "very_hard", "hours": 90, "type": "concurrency"},
            
            # Circle 5
            "cpp-module-00": {"weeks": 1, "difficulty": "easy", "hours": 15, "type": "cpp"},
            "cpp-module-01": {"weeks": 1, "difficulty": "easy", "hours": 20, "type": "cpp"},
            "cpp-module-02": {"weeks": 1, "difficulty": "medium", "hours": 25, "type": "cpp"},
            "cpp-module-03": {"weeks": 2, "difficulty": "medium", "hours": 35, "type": "cpp"},
            "cpp-module-04": {"weeks": 2, "difficulty": "hard", "hours": 45, "type": "cpp"},
            "cub3d": {"weeks": 3, "difficulty": "very_hard", "hours": 100, "type": "3d_graphics"},
            "netpractice": {"weeks": 1, "difficulty": "easy", "hours": 15, "type": "networking"},
            "minirt": {"weeks": 4, "difficulty": "very_hard", "hours": 120, "type": "ray_tracing"},
            
            # Circle 6
            "ft_irc": {"weeks": 4, "difficulty": "very_hard", "hours": 110, "type": "networking"},
            "webserv": {"weeks": 4, "difficulty": "very_hard", "hours": 130, "type": "web"},
            "inception": {"weeks": 2, "difficulty": "medium", "hours": 40, "type": "devops"},
            "cpp-module-05": {"weeks": 2, "difficulty": "hard", "hours": 50, "type": "cpp"},
            "cpp-module-06": {"weeks": 2, "difficulty": "hard", "hours": 55, "type": "cpp"},
            "cpp-module-07": {"weeks": 2, "difficulty": "hard", "hours": 60, "type": "cpp"},
            "cpp-module-08": {"weeks": 2, "difficulty": "very_hard", "hours": 70, "type": "cpp"},
            "cpp-module-09": {"weeks": 2, "difficulty": "very_hard", "hours": 75, "type": "cpp"},
            
            # Circle 7
            "ft_transcendence": {"weeks": 6, "difficulty": "very_hard", "hours": 200, "type": "fullstack"}
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
        project_time_estimates = self.get_project_time_estimates()
        
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
                # Get time estimate for this project
                time_estimate = project_time_estimates.get(project, {"weeks": 2, "difficulty": "medium", "hours": 40})
                remaining.append({
                    "name": project,
                    "slug": project.lower().replace(' ', '-'),
                    "description": f"Required for {current_circle_data.get('name', f'Circle {current_circle}')}",
                    "circle": current_circle,
                    "estimated_weeks": time_estimate["weeks"],
                    "estimated_hours": time_estimate["hours"],
                    "difficulty": time_estimate["difficulty"],
                    "type": time_estimate.get("type", "general")
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
        
        # Calculate total time needed based on realistic project estimates
        total_weeks_needed = sum(project.get("estimated_weeks", 2) for project in remaining_projects[:projects_needed])
        total_hours_needed = sum(project.get("estimated_hours", 40) for project in remaining_projects[:projects_needed])
        
        # Ensure we have valid numbers for calculations
        safe_days_remaining = max(1, days_remaining) if days_remaining is not None else 30
        safe_projects_needed = max(1, projects_needed)
        
        # Create realistic weekly plan based on project time estimates
        weekly_plan = self._create_realistic_weekly_schedule(remaining_projects, safe_days_remaining, safe_projects_needed)
        
        # Calculate if the timeline is realistic
        weeks_available = math.ceil(safe_days_remaining / 7)
        timeline_feasible = total_weeks_needed <= weeks_available
        
        escape_plan = {
            "start_date": begin_at,
            "blackhole_date": status.get("blackhole_date"),
            "days_remaining": days_remaining,
            "weeks_available": weeks_available,
            "current_circle": circle_info.get("current_circle", 0),
            "current_circle_name": circle_info.get("current_circle_name", ""),
            "next_circle": circle_info.get("next_circle"),
            "next_circle_name": circle_info.get("next_circle_name", ""),
            "projects_completed_current": circle_info.get("completed_in_current", 0),
            "projects_required_current": circle_info.get("required_in_current", 0),
            "projects_remaining_current": projects_needed,
            "total_weeks_needed": total_weeks_needed,
            "total_hours_needed": total_hours_needed,
            "timeline_feasible": timeline_feasible,
            "required_projects": safe_projects_needed,
            "weekly_schedule": weekly_plan,
            "priority_projects": [p.get("name", "Unknown") for p in remaining_projects],
            "missing_projects": missing_projects,
            "recommendations": self._generate_realistic_recommendations(
                status, days_remaining, total_weeks_needed, weeks_available, timeline_feasible
            )
        }
        
        return {
            "status": status,
            "escape_plan": escape_plan
        }
    
    def _create_realistic_weekly_schedule(self, projects: List[Dict], days_remaining: int, required_count: int) -> List[Dict]:
        """Create a realistic weekly schedule based on project time estimates"""
        if not projects:
            return []
            
        weeks_available = math.ceil(days_remaining / 7)
        projects_to_schedule = projects[:required_count]
        
        weekly_schedule = []
        current_week = 1
        scheduled_projects = []
        
        # Sort projects by estimated weeks (longest first to schedule them early)
        projects_to_schedule.sort(key=lambda x: x.get("estimated_weeks", 2), reverse=True)
        
        for project in projects_to_schedule:
            project_weeks = project.get("estimated_weeks", 2)
            project_name = project.get("name", "Unknown Project")
            project_hours = project.get("estimated_hours", 40)
            difficulty = project.get("difficulty", "medium")
            
            # Check if we can fit this project in the remaining weeks
            if current_week + project_weeks - 1 > weeks_available:
                # If not, skip this project (it won't fit in the timeline)
                continue
            
            # Schedule the project
            for week_offset in range(project_weeks):
                week_num = current_week + week_offset
                
                # Find or create the week entry
                week_entry = None
                for entry in weekly_schedule:
                    if entry["week"] == week_num:
                        week_entry = entry
                        break
                
                if not week_entry:
                    week_entry = {
                        "week": week_num,
                        "focus_projects": [],
                        "weekly_goals": [],
                        "total_hours": 0
                    }
                    weekly_schedule.append(week_entry)
                
                # Add project to this week (only once per project)
                if week_offset == 0:
                    week_entry["focus_projects"].append({
                        "name": project_name,
                        "estimated_hours": project_hours,
                        "difficulty": difficulty,
                        "total_weeks": project_weeks,
                        "week_in_progress": 1
                    })
                    week_entry["total_hours"] += project_hours // project_weeks
                else:
                    # For subsequent weeks, just mark it as ongoing
                    for existing_project in week_entry["focus_projects"]:
                        if existing_project["name"] == project_name:
                            existing_project["week_in_progress"] = week_offset + 1
                            break
            
            current_week += project_weeks
            scheduled_projects.append(project)
            
            # Stop if we've scheduled all required projects or run out of weeks
            if len(scheduled_projects) >= required_count or current_week > weeks_available:
                break
        
        # Add weekly goals and format the schedule
        for week_entry in weekly_schedule:
            focus_projects = week_entry["focus_projects"]
            ongoing_projects = [p for p in focus_projects if p.get("week_in_progress", 1) > 1]
            new_projects = [p for p in focus_projects if p.get("week_in_progress", 1) == 1]
            
            goals = []
            if new_projects:
                goals.append("Start: " + ", ".join([p["name"] for p in new_projects]))
            if ongoing_projects:
                formatted = [
                    f"{p['name']} (week {p.get('week_in_progress', 1)}/{p.get('total_weeks', 1)})"
                    for p in ongoing_projects
                ]
                goals.append("Continue: " + ", ".join(formatted))
            
            goals.extend([
                f"Target: {week_entry['total_hours']} hours of focused work",
                "Daily coding sessions: 4-6 hours",
                "Weekend: Intensive work and peer reviews"
            ])
            
            week_entry["weekly_goals"] = goals
        
        return weekly_schedule
    
    def _generate_realistic_recommendations(self, status: Dict, days_remaining: int, total_weeks_needed: int, 
                                         weeks_available: int, timeline_feasible: bool) -> List[str]:
        """Generate realistic recommendations based on project time estimates"""
        recommendations = []
        risk_level = status.get("risk_level", "UNKNOWN")
        current_level = status.get("level", 0)
        circle_info = status.get("circle_info", {})
        begin_at = status.get("begin_at")
        
        # Timeline analysis
        if not timeline_feasible:
            recommendations.extend([
                "🚨 TIMELINE CRITICAL: Your available time may not be sufficient",
                f"⏰ You need {total_weeks_needed} weeks but only have {weeks_available} weeks until black hole",
                "💡 Consider focusing on the most critical projects first",
                "🆘 Discuss timeline options with your campus staff"
            ])
        else:
            recommendations.append(f"✅ Timeline looks feasible: {total_weeks_needed} weeks needed, {weeks_available} weeks available")
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "🚨 MAXIMUM EFFORT REQUIRED!",
                "⏰ Dedicate 6-8 hours daily to coding (40-50 hours/week)",
                "🎯 Focus on one project at a time to maximize efficiency",
                "🆘 Seek immediate help from staff and senior students",
                "📞 Daily check-ins with your tutor or referent"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ HIGH INTENSITY NEEDED",
                "⏰ Dedicate 4-6 hours daily (30-40 hours/week)",
                "👥 Form dedicated study groups for each project",
                "📊 Track progress daily and adjust plan weekly",
                "🎯 Prioritize projects by circle progression impact"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "🔶 CONSISTENT EFFORT REQUIRED",
                "⏰ Dedicate 3-4 hours daily (20-30 hours/week)",
                "👥 Regular peer programming sessions",
                "📈 Weekly progress reviews and plan adjustments",
                "💡 Balance project work with skill development"
            ])
        else:
            recommendations.extend([
                "✅ STEADY PACE MAINTAINED",
                "⏰ 2-3 hours of focused coding daily (15-20 hours/week)",
                "👥 Help peers and reinforce learning through teaching",
                "🚀 Challenge yourself with bonus objectives"
            ])
        
        # Add circle-specific advice
        current_circle = circle_info.get("current_circle", 0)
        completed_in_current = circle_info.get("completed_in_current", 0)
        required_in_current = circle_info.get("required_in_current", 0)
        
        recommendations.append(f"🎯 You are in Circle {current_circle}: {completed_in_current}/{required_in_current} projects completed")
        
        # Project-specific time management advice
        if current_circle >= 4:
            recommendations.extend([
                "⏳ Complex projects ahead: Plan for 3-4 week timelines",
                "🔧 Break large projects into smaller milestones",
                "📝 Document your progress and challenges",
                "🔄 Regular code reviews with peers"
            ])
        
        # Time management strategies
        recommendations.extend([
            "📅 Use time blocking: Dedicate specific hours each day to coding",
            "🎯 Set weekly milestones with clear deliverables",
            "🔄 Review and adjust your plan every Sunday",
            "⏰ Track actual time spent vs estimated time"
        ])
        
        # Add black hole specific info
        if begin_at:
            try:
                start_date = datetime.fromisoformat(begin_at.replace('Z', '+00:00'))
                days_since_start = (datetime.now().astimezone() - start_date).days
                recommendations.append(f"📅 Started: {start_date.date()} ({days_since_start} days ago)")
            except:
                pass
        
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
            print(f"\n📝 REALISTIC ESCAPE PLAN")
            if 'message' in plan:
                print(plan['message'])
            else:
                print(f"🎯 Required Projects for Circle {plan.get('current_circle')}: {plan.get('projects_remaining_current', 0)}")
                print(f"⏰ Total Time Needed: {plan.get('total_weeks_needed', 0)} weeks ({plan.get('total_hours_needed', 0)} hours)")
                print(f"📅 Weeks Available: {plan.get('weeks_available', 0)} weeks")
                print(f"📈 Timeline Feasible: {'✅ YES' if plan.get('timeline_feasible') else '❌ NO'}")
                
                # Show exactly which projects are missing with time estimates
                missing_projects = plan.get('missing_projects', [])
                if missing_projects:
                    print(f"\n🎯 PROJECTS NEEDED FOR CIRCLE {plan.get('current_circle')}:")
                    for i, project in enumerate(missing_projects, 1):
                        time_est = escape_system.get_project_time_estimates().get(project, {"weeks": 2, "hours": 40})
                        print(f"  {i}. {project} - {time_est['weeks']} weeks, {time_est['hours']} hours ({time_est['difficulty']})")
                
                weekly_schedule = plan.get('weekly_schedule', [])
                if weekly_schedule:
                    print(f"\n📅 REALISTIC WEEKLY SCHEDULE:")
                    for week in weekly_schedule:
                        print(f"\nWeek {week.get('week', '?')}:")
                        for project in week.get('focus_projects', []):
                            status = f" (Week {project.get('week_in_progress', 1)}/{project.get('total_weeks', 2)})" if project.get('total_weeks', 2) > 1 else ""
                            print(f"   • {project.get('name', 'Unknown')}{status} - {project.get('estimated_hours', 0)} hours ({project.get('difficulty', 'medium')})")
                        for goal in week.get('weekly_goals', []):
                            print(f"   🎯 {goal}")
            
            recommendations = plan.get('recommendations', [])
            if recommendations:
                print(f"\n💡 REALISTIC RECOMMENDATIONS:")
                for rec in recommendations:
                    print(f"  • {rec}")
            
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()