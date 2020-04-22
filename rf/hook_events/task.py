def update_task_details(doc, method):
    if doc.github_pr and not doc.db_get("github_pr"):
        doc.status = "Needs Code Review"
