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
        
        # Extract black hole information with safe parsing
        blackholed_at = main_cursus.get('blackholed_at')
        begin_at = main_cursus.get('begin_at')
        grade = main_cursus.get('grade')
        level = main_cursus.get('level', 0)
        cursus_id = main_cursus.get('cursus_id')
        cursus_name = main_cursus.get('cursus', {}).get('name', 'Unknown Cursus')
        
        # Get user's projects
        user_projects = self.get_user_projects(user_id)
        
        # Get cursus projects to understand what's remaining
        cursus_projects = []
        if cursus_id:
            cursus_projects = self.get_cursus_projects(cursus_id)
        
        # Calculate current status with safe date handling
        current_date = datetime.now().astimezone()
        
        blackhole_date = None
        days_until_blackhole = None
        is_blackholed = False
        
        if blackholed_at:
            try:
                blackhole_date = datetime.fromisoformat(blackholed_at.replace('Z', '+00:00'))
                days_until_blackhole = (blackhole_date - current_date).days
                is_blackholed = days_until_blackhole <= 0 if days_until_blackhole is not None else False
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error parsing blackhole date: {e}")
        
        # Calculate projects information
        completed_projects = self._get_completed_projects(user_projects)
        remaining_projects = self._get_remaining_projects(completed_projects, cursus_projects)
        
        # Calculate circle progress (assuming common 42 structure)
        circle_info = self._calculate_circle_progress(completed_projects, level)
        
        # Calculate risk level safely
        risk_level = self._calculate_risk_level(days_until_blackhole, level)
        
        return {
            "user_login": user_info.get("login"),
            "user_name": user_info.get("displayname"),
            "cursus": cursus_name,
            "grade": grade,
            "level": level,
            "begin_at": begin_at,
            "blackholed_at": blackholed_at,
            "blackhole_date": blackhole_date.isoformat() if blackhole_date else None,
            "days_until_blackhole": days_until_blackhole,
            "is_blackholed": is_blackholed,
            "total_completed": len(completed_projects),
            "circle_info": circle_info,
            "remaining_projects": remaining_projects,
            "risk_level": risk_level
        }
    
    def _get_completed_projects(self, projects_users: List[Dict]) -> List[Dict]:
        """Get completed and validated projects"""
        completed = []
        for project_user in projects_users:
            if not isinstance(project_user, dict):
                continue
                
            status = project_user.get("status", "")
            marked_at = project_user.get("marked_at")
            final_mark = project_user.get("final_mark", 0)
            
            # Safely check if project is completed
            if status in ["finished", "success"] and final_mark is not None and final_mark >= 50:
                project_data = project_user.get("project", {})
                if project_data:
                    completed.append({
                        "id": project_data.get("id"),
                        "name": project_data.get("name"),
                        "slug": project_data.get("slug"),
                        "completed_at": marked_at,
                        "final_mark": final_mark,
                        "status": status,
                        "cursus_ids": project_data.get('cursus_ids', [])
                    })
        return completed
    
    def _get_remaining_projects(self, completed_projects: List[Dict], cursus_projects: List[Dict]) -> List[Dict]:
        """Get projects that the user hasn't completed yet"""
        completed_ids = {p["id"] for p in completed_projects if p.get("id") is not None}
        remaining = []
        
        for project in cursus_projects:
            if not isinstance(project, dict):
                continue
                
            project_id = project.get("id")
            if project_id is None:
                continue
                
            if project_id not in completed_ids:
                # Filter out exams and special projects
                name = project.get("name", "").lower()
                if any(excl in name for excl in ['exam', 'piscine', 'rush', 'interview']):
                    continue
                    
                remaining.append({
                    "id": project_id,
                    "name": project.get("name"),
                    "slug": project.get("slug"),
                    "difficulty": project.get("difficulty", 0),
                    "description": project.get("description", "")
                })
        
        # Sort by difficulty (easier first) with safe comparison
        remaining.sort(key=lambda x: x.get("difficulty", 0) or 0)
        return remaining
    
    def _calculate_circle_progress(self, completed_projects: List[Dict], current_level: float) -> Dict:
        """
        Calculate circle progress based on completed projects and level
        This is an approximation since exact circle rules vary
        """
        # Ensure current_level is a valid number
        safe_level = current_level if current_level is not None else 0
        
        # Common 42 circle structure (adjust based on your campus)
        circle_thresholds = [
            {"circle": 0, "level": 0, "projects_required": 0},
            {"circle": 1, "level": 3.0, "projects_required": 5},
            {"circle": 2, "level": 7.0, "projects_required": 10},
            {"circle": 3, "level": 10.0, "projects_required": 15},
            {"circle": 4, "level": 13.0, "projects_required": 20},
            {"circle": 5, "level": 16.0, "projects_required": 25},
        ]
        
        current_circle = 0
        next_circle = None
        projects_to_next_circle = 0
        level_to_next_circle = 0
        
        for i, threshold in enumerate(circle_thresholds):
            threshold_level = threshold.get("level", 0)
            if safe_level >= threshold_level:
                current_circle = threshold.get("circle", 0)
                if i + 1 < len(circle_thresholds):
                    next_threshold = circle_thresholds[i + 1]
                    next_circle = next_threshold.get("circle")
                    projects_required = next_threshold.get("projects_required", 0)
                    projects_to_next_circle = max(0, projects_required - len(completed_projects))
                    level_to_next_circle = next_threshold.get("level", 0) - safe_level
            else:
                break
        
        # Calculate level progress safely
        level_progress = round((safe_level % 1) * 100, 1) if safe_level is not None else 0
        
        return {
            "current_circle": current_circle,
            "next_circle": next_circle,
            "projects_to_next_circle": projects_to_next_circle,
            "level_to_next_circle": round(level_to_next_circle, 2),
            "level_progress": level_progress
        }
    
    def _calculate_risk_level(self, days_until_blackhole: Optional[int], current_level: float) -> str:
        """Calculate risk level based on black hole date and progress"""
        # Handle None values safely
        if days_until_blackhole is None:
            return "UNKNOWN"
        
        safe_days = days_until_blackhole if days_until_blackhole is not None else float('inf')
        safe_level = current_level if current_level is not None else 0
        
        if safe_days <= 0:
            return "BLACK_HOLED"
        elif safe_days <= 30:
            return "CRITICAL"
        elif safe_days <= 90:
            return "HIGH"
        elif safe_days <= 180:
            return "MEDIUM"
        elif safe_level < 3.0 and safe_days <= 270:
            return "LOW"  # New students have more time
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
        
        if days_remaining is None:
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
        
        # Calculate required pace safely
        next_circle = circle_info.get("next_circle")
        if next_circle is not None:
            projects_needed = circle_info.get("projects_to_next_circle", 0)
            level_needed = circle_info.get("level_to_next_circle", 0)
        else:
            # Generic calculation based on remaining time
            projects_needed = max(5, len(remaining_projects) // 2)
            level_needed = 1.0
        
        # Ensure we have valid numbers for calculations
        safe_days_remaining = max(1, days_remaining) if days_remaining is not None else 30
        safe_projects_needed = max(1, projects_needed) if projects_needed is not None else 5
        
        weekly_pace = math.ceil(safe_projects_needed / max(1, safe_days_remaining / 7))
        daily_pace = safe_projects_needed / safe_days_remaining
        
        # Create weekly plan
        weekly_plan = self._create_weekly_schedule(remaining_projects, safe_days_remaining, safe_projects_needed)
        
        escape_plan = {
            "blackhole_date": status.get("blackhole_date"),
            "days_remaining": days_remaining,
            "current_circle": circle_info.get("current_circle", 0),
            "next_circle": next_circle,
            "projects_to_next_circle": circle_info.get("projects_to_next_circle", 0),
            "level_to_next_circle": circle_info.get("level_to_next_circle", 0),
            "required_projects": safe_projects_needed,
            "recommended_weekly_pace": weekly_pace,
            "recommended_daily_pace": f"{daily_pace:.2f} projects per day",
            "weekly_schedule": weekly_plan,
            "priority_projects": [p.get("name", "Unknown") for p in remaining_projects[:5]],
            "recommendations": self._generate_recommendations(status, days_remaining, weekly_pace)
        }
        
        return {
            "status": status,
            "escape_plan": escape_plan
        }
    
    def _create_weekly_schedule(self, projects: List[Dict], days_remaining: int, required_count: int) -> List[Dict]:
        """Create a weekly study schedule"""
        weeks = math.ceil(days_remaining / 7) if days_remaining else 4
        projects_per_week = math.ceil(required_count / max(1, weeks))
        
        weekly_schedule = []
        project_index = 0
        
        for week in range(1, weeks + 1):
            week_projects = projects[project_index:project_index + projects_per_week]
            project_index += len(week_projects)
            
            if week_projects:
                weekly_schedule.append({
                    "week": week,
                    "target_projects": len(week_projects),
                    "projects": [
                        {
                            "name": p.get("name", "Unknown Project"), 
                            "difficulty": p.get("difficulty", 0) or 0
                        } for p in week_projects
                    ],
                    "weekly_goals": [
                        f"Complete {len(week_projects)} projects",
                        f"Focus on: {', '.join([p.get('name', 'Unknown') for p in week_projects[:2]])}",
                        "Attend peer learning sessions",
                        "Review progress mid-week"
                    ]
                })
            
            if project_index >= len(projects):
                break
        
        return weekly_schedule
    
    def _generate_recommendations(self, status: Dict, days_remaining: Optional[int], weekly_pace: int) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        risk_level = status.get("risk_level", "UNKNOWN")
        current_level = status.get("level", 0)
        
        if risk_level == "CRITICAL":
            recommendations.extend([
                "🚨 CRITICAL: Maximum effort required!",
                "🎯 Focus exclusively on project completion",
                "⏰ Dedicate 6-8 hours daily to coding",
                "🆘 Seek immediate help from staff and peers",
                "📞 Schedule regular check-ins with your tutor"
            ])
        elif risk_level == "HIGH":
            recommendations.extend([
                "⚠️ HIGH RISK: Significant effort needed",
                "🎯 Prioritize project completion over everything",
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
                "👥 Help peers and reinforce learning",
                "🚀 Challenge yourself with advanced projects"
            ])
        
        # Level-specific advice
        safe_level = current_level if current_level is not None else 0
        if safe_level < 3.0:
            recommendations.extend([
                "🌱 Beginner: Master the fundamentals",
                "💡 Focus on understanding core concepts",
                "🔁 Practice with small exercises daily"
            ])
        elif safe_level < 7.0:
            recommendations.extend([
                "🚀 Intermediate: Build complex systems",
                "💡 Focus on architecture and design",
                "🔧 Learn debugging and optimization"
            ])
        else:
            recommendations.extend([
                "🎯 Advanced: Specialize and excel",
                "💡 Focus on advanced concepts",
                "🌟 Consider mentoring newer students"
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
        print(f"⭐ Grade: {status.get('grade', 'Not assigned')}")
        print(f"📈 Level: {status.get('level', 'Unknown')}")
        print(f"🎯 Risk Level: {status.get('risk_level', 'UNKNOWN')}")
        
        blackhole_date = status.get('blackhole_date')
        if blackhole_date:
            print(f"⏰ Black Hole Date: {blackhole_date}")
            print(f"📆 Days Remaining: {status.get('days_until_blackhole', 'Unknown')}")
        else:
            print(f"⏰ Black Hole Date: Not set (safe for now)")
        
        print(f"✅ Projects Completed: {status.get('total_completed', 0)}")
        
        circle_info = status.get('circle_info', {})
        print(f"🔄 Current Circle: {circle_info.get('current_circle', 0)}")
        
        next_circle = circle_info.get('next_circle')
        if next_circle is not None:
            print(f"🎯 Next Circle: {next_circle}")
            print(f"📊 Projects to Next Circle: {circle_info.get('projects_to_next_circle', 0)}")
            print(f"📈 Level to Next Circle: {circle_info.get('level_to_next_circle', 0)}")
        
        if plan:
            print(f"\n📝 PERSONALIZED ESCAPE PLAN")
            if 'message' in plan:
                print(plan['message'])
            else:
                print(f"🎯 Required Projects: {plan.get('required_projects', 0)}")
                print(f"📈 Recommended Pace: {plan.get('recommended_daily_pace', 'N/A')}")
                print(f"📅 Weekly Target: {plan.get('recommended_weekly_pace', 0)} projects/week")
                
                weekly_schedule = plan.get('weekly_schedule', [])
                if weekly_schedule:
                    print(f"\n📅 WEEKLY ACTION PLAN")
                    for week in weekly_schedule:
                        print(f"\nWeek {week.get('week', '?')}: {week.get('target_projects', 0)} projects")
                        for project in week.get('projects', []):
                            print(f"   • {project.get('name', 'Unknown')} (difficulty: {project.get('difficulty', 'N/A')})")
            
            priority_projects = plan.get('priority_projects', [])
            if priority_projects:
                print(f"\n🎯 PRIORITY PROJECTS")
                for i, project in enumerate(priority_projects[:5], 1):
                    print(f"  {i}. {project}")
            
            recommendations = plan.get('recommendations', [])
            if recommendations:
                print(f"\n💡 EXPERT RECOMMENDATIONS")
                for rec in recommendations:
                    print(f"  • {rec}")
            
    except Exception as e:
        print(f"❌ System error: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔧 Make sure to:")
        print("1. Replace CLIENT_ID and CLIENT_SECRET with your actual credentials")
        print("2. Use a valid 42 student login")
        print("3. Check your application has proper API permissions")

if __name__ == "__main__":
    main()