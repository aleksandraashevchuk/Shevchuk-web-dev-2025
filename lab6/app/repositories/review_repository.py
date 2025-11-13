from ..models import Review
from sqlalchemy import desc, asc
from datetime import datetime

class ReviewRepository:
    def __init__(self, db):
        self.db = db

    def get_course_reviews(self, course_id, page=None, per_page=5, order_by='newest'):
        query = self.db.session.query(Review).filter_by(course_id=course_id)

        if order_by == 'newest':
            query = query.order_by(desc(Review.created_at))
        elif order_by == 'positive':
            query = query.order_by(desc(Review.rating), desc(Review.created_at))
        elif order_by == 'negative':
            query = query.order_by(asc(Review.rating), desc(Review.created_at))

        if page is not None:
            return query.paginate(page=page, per_page=per_page, error_out=False)
        return query.all()

    def get_last_reviews(self, course_id, limit=5):
        return (self.db.session.query(Review)
                .filter_by(course_id=course_id)
                .order_by(desc(Review.created_at))
                .limit(limit)
                .all())

    def get_pagination_info(self, course_id, per_page=5):
        count = self.db.session.query(Review).filter_by(course_id=course_id).count()
        return {
            'total': count,
            'per_page': per_page,
            'pages': (count + per_page - 1) // per_page
        }

    def get_user_review(self, course_id, user_id):
        return self.db.session.query(Review).filter_by(
            course_id=course_id,
            user_id=user_id
        ).first()

    def add_review(self, course_id, user_id, rating, text):
        review = Review(
            rating=rating,
            text=text,
            course_id=course_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        self.db.session.add(review)
        return review