from website import create_app, db
from website.models import Category

app = create_app()

@app.context_processor
def inject_categories(): #To make categories available for every page (mainly the categories dropdown)
    categories = db.session.execute(db.select(Category)).scalars().all()
    return dict(categories=categories)

if __name__ == '__main__':
    app.run()

    