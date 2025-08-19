from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

# ===================================================================
# Forum Category Endpoints
# ===================================================================

@router.post("/categories/", response_model=schemas.ForumCategory, status_code=status.HTTP_201_CREATED)
def create_forum_category(
    *,
    db: Session = Depends(deps.get_db),
    category_in: schemas.ForumCategoryCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create new forum category. (Superusers only)"""
    category = crud.forum_category.get_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(
            status_code=400,
            detail="A category with this name already exists.",
        )
    return crud.forum_category.create(db, obj_in=category_in)

@router.get("/categories/", response_model=List[schemas.ForumCategory])
def read_forum_categories(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all forum categories."""
    return crud.forum_category.get_multi(db, skip=skip, limit=limit)

@router.put("/categories/{category_id}", response_model=schemas.ForumCategory)
def update_forum_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    category_in: schemas.ForumCategoryUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Update a forum category. (Superusers only)"""
    category = crud.forum_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Uniqueness check for name to avoid IntegrityError
    upd = category_in.model_dump(exclude_unset=True)
    new_name = upd.get("name")
    if new_name and new_name != category.name:
        existing = crud.forum_category.get_by_name(db, name=new_name)
        if existing and existing.id != category.id:
            raise HTTPException(status_code=400, detail="A category with this name already exists.")
    return crud.forum_category.update(db, db_obj=category, obj_in=category_in)

@router.delete("/categories/{category_id}", response_model=schemas.ForumCategory)
def delete_forum_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a forum category. (Superusers only)
    """
    category = crud.forum_category.get(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.forum_category.remove(db=db, id=category_id)
    return category

# ===================================================================
# Forum Topic Endpoints
# ===================================================================

@router.get("/topics/", response_model=List[schemas.ForumTopic])
def read_all_forum_topics(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all forum topics across all categories."""
    return crud.forum_topic.get_multi(db, skip=skip, limit=limit)

@router.post("/topics/", response_model=schemas.ForumTopic, status_code=status.HTTP_201_CREATED)
def create_forum_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_in: schemas.ForumTopicCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a new forum topic with its initial post."""
    category = crud.forum_category.get(db, id=topic_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    topic = crud.forum_topic.create_with_initial_post(db, obj_in=topic_in, author=current_user)
    return topic

@router.get("/categories/{category_id}/topics", response_model=List[schemas.ForumTopic])
def read_topics_in_category(
    category_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all topics within a specific category."""
    category = crud.forum_category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.forum_topic.get_multi_by_category(db, category_id=category_id, skip=skip, limit=limit)

@router.get("/topics/{topic_id}", response_model=schemas.ForumTopic)
def read_forum_topic(
    topic_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Retrieve a specific topic by ID, including its posts."""
    topic = crud.forum_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=schemas.ForumTopic)
def update_forum_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: int,
    topic_in: schemas.ForumTopicUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Update a forum topic."""
    topic = crud.forum_topic.get(db, id=topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    if not crud.user.is_superuser(current_user) and (topic.author_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return crud.forum_topic.update(db, db_obj=topic, obj_in=topic_in)

@router.delete("/topics/{topic_id}", response_model=schemas.ForumTopic)
def delete_forum_topic(
    *,
    db: Session = Depends(deps.get_db),
    topic_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a forum topic. (Author or Superusers only)
    """
    # Eagerly load relationships to prevent DetachedInstanceError on return
    topic = db.query(models.ForumTopic).options(
        joinedload(models.ForumTopic.author),
        joinedload(models.ForumTopic.category)
    ).filter(models.ForumTopic.id == topic_id).first()

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if not crud.user.is_superuser(current_user) and (topic.author_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db.delete(topic)
    db.commit()
    return topic

# ===================================================================
# Forum Post Endpoints
# ===================================================================

@router.post("/posts/", response_model=schemas.ForumPost, status_code=status.HTTP_201_CREATED)
def create_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    post_in: schemas.ForumPostCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Create a new post in a topic (a reply)."""
    topic = crud.forum_topic.get(db, id=post_in.topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    if topic.is_closed:
        raise HTTPException(status_code=403, detail="This topic is closed.")
    
    post = crud.forum_post.create_with_owner(db, obj_in=post_in, author_id=current_user.id)

    # Send notification to the topic author if the replier is not the author
    if topic.author_id != current_user.id:
        crud.notification.create_forum_reply_notification(
            db=db,
            recipient_user_id=topic.author_id,
            topic_id=topic.id,
            topic_title=topic.title,
            reply_author_name=current_user.email
        )

    return post

@router.put("/posts/{post_id}", response_model=schemas.ForumPost)
def update_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    post_in: schemas.ForumPostUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Update a user's own post."""
    post = crud.forum_post.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not crud.user.is_superuser(current_user) and (post.author_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    post.is_edited = True
    return crud.forum_post.update(db, db_obj=post, obj_in=post_in)

@router.delete("/posts/{post_id}", response_model=schemas.ForumPost)
def delete_forum_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete a user's own post."""
    post = crud.forum_post.get(db, id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not crud.user.is_superuser(current_user) and (post.author_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud.forum_post.remove(db, id=post_id)
