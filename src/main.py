from website import create_app, db

if __name__ == '__main__':
    app = create_app()
    app.run()


# Shouldn't need to use unless a fresh DB is required
def CreateDB():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    db.create_all()