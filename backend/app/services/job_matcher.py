from typing import List, Dict, Any, Optional

def normalize_skill_name(skill: str) -> str:
    """Normalize skill string for case-insensitive matching."""
    if not skill:
        return ""
    # Strip whitespace and common punctuation differences
    cleaned = skill.strip().lower()
    if cleaned in ["react.js", "reactjs"]:
        return "react"
    if cleaned in ["node", "nodejs"]:
        return "node.js"
    if cleaned in ["postgres"]:
        return "postgresql"
    return cleaned

def remove_duplicate_skills(skills: Optional[List[str]]) -> List[str]:
    """
    Remove case-insensitive duplicates while preserving original stripped casing.
    """
    if not skills:
        return []
    seen = set()
    result = []
    for s in skills:
        if not s or not isinstance(s, str):
            continue
        clean = s.strip()
        norm = normalize_skill_name(clean)
        if norm and norm not in seen:
            seen.add(norm)
            result.append(clean)
    return result

def normalize_job_skills(skills: Optional[List[str]]) -> List[str]:
    """
    Normalizes, cleans, and deduplicates job skill requirements.
    """
    return remove_duplicate_skills(skills)

def calculate_job_match(
    required_skills: Optional[List[str]],
    student_skills: Optional[List[str]],
    job_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Transparent rule-based job matching algorithm.
    Formula:
      match_percentage = (number of matched required skills / total required skills) * 100
    """
    req_list = required_skills or []
    std_list = student_skills or []

    # Filter out empty or non-string items
    req_clean = [s.strip() for s in req_list if isinstance(s, str) and s.strip()]
    std_clean = [s.strip() for s in std_list if isinstance(s, str) and s.strip()]

    if not req_clean:
        return {
            "job_id": job_id,
            "match_percentage": 100,
            "matched_skills": [],
            "missing_skills": []
        }

    # Map student skills by normalized form
    student_skill_map = {normalize_skill_name(s): s for s in std_clean}

    matched_skills = []
    missing_skills = []

    for req_skill in req_clean:
        norm_req = normalize_skill_name(req_skill)
        if norm_req in student_skill_map:
            matched_skills.append(req_skill)
        else:
            missing_skills.append(req_skill)

    matched_count = len(matched_skills)
    total_count = len(req_clean)

    match_percentage = round((matched_count / total_count) * 100) if total_count > 0 else 100

    return {
        "job_id": job_id,
        "match_percentage": match_percentage,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }
