from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy import desc
from datetime import date
from app import db
from models import Project, RewardTier, Pledge

proj_bp = Blueprint("proj", __name__)

@proj_bp.route("/")
def project_list():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    sort = request.args.get("sort", "newest")  

    qry = Project.query
    if q:
        qry = qry.filter(Project.name.ilike(f"%{q}%"))
    if category:
        qry = qry.filter(Project.category == category)

    if sort == "ending":
        qry = qry.order_by(Project.deadline.asc())
    elif sort == "mostfunded":
        qry = qry.order_by(desc(Project.current_amount))
    else:
        qry = qry.order_by(desc(Project.project_id)) 

    projects = qry.all()
    categories = [c[0] for c in db.session.query(Project.category).distinct().all()]
    return render_template("index.html", projects=projects, categories=categories, q=q, category=category, sort=sort)

@proj_bp.route("/project/<int:pid>", methods=["GET"])
def project_detail(pid):
    project = Project.query.get_or_404(pid)
    tiers = RewardTier.query.filter_by(project_id=pid).order_by(RewardTier.minimum_fund.asc()).all()
    pledges = Pledge.query.filter_by(project_id=pid).all()   # NEW
    return render_template("detail.html", project=project, tiers=tiers, pledges=pledges)


@proj_bp.route("/project/<int:pid>/pledge", methods=["POST"])
def pledge(pid):
    project = Project.query.get_or_404(pid)
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    amount = int(request.form.get("amount", "0") or "0")
    tier_id = request.form.get("tier_id", "")
    tier = RewardTier.query.get(int(tier_id)) if tier_id else None

    if project.deadline <= date.today():
        project.rejection_count += 1
        db.session.commit()
        flash("Pledge rejected: project deadline has passed.", "danger")
        return redirect(url_for("proj.project_detail", pid=pid))

    if tier and amount < tier.minimum_fund:
        project.rejection_count += 1
        db.session.commit()
        flash("Pledge rejected: amount is below selected reward tier minimum.", "danger")
        return redirect(url_for("proj.project_detail", pid=pid))

    if tier and tier.quota_remaining <= 0:
        project.rejection_count += 1
        db.session.commit()
        flash("Pledge rejected: reward tier is out of stock.", "danger")
        return redirect(url_for("proj.project_detail", pid=pid))

    pledge = Pledge(user_id=session["user_id"], project_id=pid, amount=amount, reward_tier_id=(tier.id if tier else None), success=True)
    project.current_amount += amount
    if tier:
        tier.quota_remaining -= 1
    db.session.add(pledge)
    db.session.commit()
    flash("Thank you for supporting!", "success")
    return redirect(url_for("proj.project_detail", pid=pid))

@proj_bp.route("/stats")
def stats():
    projects = Project.query.all()
    success = sum(1 for p in projects if p.is_success())
    failed = sum(1 for p in projects if p.is_failed())
    return render_template("stats.html", success=success, failed=failed, projects=projects)
