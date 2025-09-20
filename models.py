from datetime import datetime, date
from random import randint

from app import db

def gen_project_id():
    # 8 digits, first digit non-zero
    first = randint(1, 9)
    rest = randint(0, 999_9999)  # 7 digits
    return int(f"{first}{rest:07d}")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)  # plain for demo
    pledges = db.relationship("Pledge", backref="user", lazy=True)

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True, default=gen_project_id)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    goal = db.Column(db.Integer, nullable=False)              # Amount > 0
    deadline = db.Column(db.Date, nullable=False)             # must be future on create
    current_amount = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, default="")
    rejection_count = db.Column(db.Integer, default=0)

    reward_tiers = db.relationship("RewardTier", backref="project", lazy=True, cascade="all, delete-orphan")
    pledges = db.relationship("Pledge", backref="project", lazy=True, cascade="all, delete-orphan")

    def progress_pct(self):
        return min(100, int(100 * self.current_amount / self.goal)) if self.goal else 0

    def is_finished(self):
        return date.today() > self.deadline

    def is_success(self):
        return self.is_finished() and self.current_amount >= self.goal

    def is_failed(self):
        return self.is_finished() and self.current_amount < self.goal

class RewardTier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    minimum_fund = db.Column(db.Integer, nullable=False)
    quota_remaining = db.Column(db.Integer, nullable=False)

class Pledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Integer, nullable=False)
    reward_tier_id = db.Column(db.Integer, db.ForeignKey("reward_tier.id"), nullable=True)
    success = db.Column(db.Boolean, default=True)
