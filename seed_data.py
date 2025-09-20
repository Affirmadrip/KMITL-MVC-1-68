from datetime import date, timedelta
from random import randint, choice
from app import create_app, db
from models import User, Project, RewardTier, Pledge

app = create_app()
with app.app_context():
    db.drop_all(); db.create_all()

    users = []
    for i in range(1, 11):
        u = User(username=f"user{i}", password=f"pass{i}")
        db.session.add(u); users.append(u)

    categories = ["Tech", "Art", "Games", "Music"]
    projects = []
    for i in range(1, 9+1):
        p = Project(
            name=f"Project {i}",
            category=choice(categories),
            goal=randint(50_000, 200_000),

            deadline=(date.today() + timedelta(days=randint(-7, 30))),
            description="Sample project for crowdfunding assignment.",
            current_amount=0
        )
        db.session.add(p); projects.append(p)
    db.session.commit()

    for p in projects:
        base = randint(500, 2000)
        for j in range(2, choice([3,3,2])+1):
            t = RewardTier(project_id=p.project_id,
                           name=f"Tier {j-1}",
                           minimum_fund=base * (j-1),
                           quota_remaining=randint(2, 10))
            db.session.add(t)
    db.session.commit()

    for _ in range(60):
        u = choice(users)
        p = choice(projects)
        tiers = RewardTier.query.filter_by(project_id=p.project_id).all()
        pick_tier = choice([None] + tiers)
        amount = randint(200, 5000)

        valid = True
        if p.deadline <= date.today():
            p.rejection_count += 1; valid = False
        elif pick_tier and amount < pick_tier.minimum_fund:
            p.rejection_count += 1; valid = False
        elif pick_tier and pick_tier.quota_remaining <= 0:
            p.rejection_count += 1; valid = False

        if valid:
            pledge = Pledge(user_id=u.id, project_id=p.project_id,
                            amount=amount, reward_tier_id=(pick_tier.id if pick_tier else None), success=True)
            p.current_amount += amount
            if pick_tier: pick_tier.quota_remaining -= 1
            db.session.add(pledge)

    db.session.commit()
    print("Seeded: users, projects, tiers, pledges.")
