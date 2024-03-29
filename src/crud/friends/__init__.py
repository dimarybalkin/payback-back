from .. import CRUDBase, Session, UserNotFoundException, CannotAddHimselfToFriendsException, UserAlreadyYourFriendException
import sqlalchemy as q
from ..db_models import FriendDatabaseModel, UserDatabaseModel
from .models import *
from utils import throws, PaginateContent, PaginateContentParams
class FriendsCRUD(CRUDBase):
    @classmethod
    @throws([
        UserNotFoundException,
        UserAlreadyYourFriendException,
        CannotAddHimselfToFriendsException,
    ])
    def add(cls, db: Session, sender_id: int, recipient_id: int) -> FriendDatabaseModel:
        if sender_id == recipient_id:
            raise CannotAddHimselfToFriendsException()
        check_user_exists = db.query(UserDatabaseModel).where(q.or_(
            UserDatabaseModel.id == sender_id,
            UserDatabaseModel.id == recipient_id,
        )).count() == 2
        if not check_user_exists:
            raise UserNotFoundException()

        invite: FriendDatabaseModel | None = db.query(FriendDatabaseModel).where(q.or_(
            FriendDatabaseModel.sender_id == sender_id & FriendDatabaseModel.recipient_id == recipient_id,
            FriendDatabaseModel.sender_id == recipient_id & FriendDatabaseModel.recipient_id == sender_id,
        )).first()
        if invite is None:
            # Send invite
            n = FriendDatabaseModel(sender_id=sender_id, recipient_id=recipient_id)
            db.add(n)
            db.commit()
            db.refresh(n)
            return n
        if invite.status:
            raise UserAlreadyYourFriendException()
        invite.status = True
        db.commit()
        db.refresh(invite)
        return invite
    @classmethod
    @throws([

    ])
    def get(cls,
            db: Session,
            user: UserDatabaseModel,
            page: PaginateContentParams) -> PaginateContent[FriendDatabaseModel]:
        crit = q.and_(
            FriendDatabaseModel.status == True, q.or_(
                FriendDatabaseModel.sender_id == user.id,
                FriendDatabaseModel.recipient_id == user.id
            )
        )
        friends = db.query(FriendDatabaseModel)\
            .where(crit)\
            .order_by(FriendDatabaseModel.id)\
            .limit(page.count)\
            .offset(page.offset)\
            .all()
        total = db.query(FriendDatabaseModel).where(crit).count()
        return PaginateContent[FriendDatabaseModel](
            result=friends,
            count=len(friends),
            total=total,
        )


