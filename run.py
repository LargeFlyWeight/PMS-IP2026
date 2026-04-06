from pms import create_app
from pms.extensions import db
from pms.seed import seed_if_empty

app = create_app()

with app.app_context():
    db.create_all()
    seed_if_empty()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
