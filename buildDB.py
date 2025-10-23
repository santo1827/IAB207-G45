# Shouldn't need to use unless a fresh DB is required
from website import create_app, db
from website.models import User, Event, Review, Category
def PopulateDB():
    categories = [
        Category(name='Yoga', description='Improve flexibility, strength and mindfulness', icon='bi-flower1'),
        Category(name='Running', description='Outdoor and indoor running activites', icon='bi-activity'),
        Category(name='BodyBuilding', description='Strength and muscle growth training', icon='bi-trophy'),
        Category(name='Powerlifting', description='Competitive strength lifting - squat, bench, deadlift', icon='bi-trophy-fill'),
        Category(name='Swimming', description='Pool or open water swimming sessions', icon='bi-water'),
        Category(name='Cycling', description='Indoor or outdoor cycling events', icon='bi-bicycle'),
        Category(name='HIIT', description='High Intensity Interval Training', icon='bi-lightning'),
        Category(name='Cross-training', description='Outdoor or indoor cross-training events', icon='bi-grid-1x2'),
    ]
    db.session.add_all(categories)

    users = [
        User(name='Tiernan', email='n10596381@qut.edu.au', phone='+6140000000', password_hash='$2b$12$zhvAWF9uhRzxvwqu4WxF6.uvXFZXTodf7btA2f.KHFQz3l3owQozS')
    ]
    db.session.add_all(users)
    
    db.session.commit()

def CreateDB():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.create_all()

CreateDB()
PopulateDB()