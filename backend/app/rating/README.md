# Rating Module

The Rating module manages product and service ratings, reviews, and feedback in the 3D Store application, providing comprehensive rating and review capabilities.

## Overview

This module handles:
- Product and service rating management
- Customer review and feedback collection
- Rating aggregation and analytics
- Review moderation and content filtering
- Rating-based recommendations
- Review sentiment analysis
- Rating reporting and insights

## Module Structure

```
rating/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Rating
Main rating entity with the following key attributes:
- **Basic Info**: `rating_id`, `customer_id`, `product_id`, `order_id`
- **Rating Details**: `rating_value`, `rating_type`, `rating_category`
- **Review**: `review_text`, `review_title`, `is_verified_purchase`
- **Status**: `status`, `is_approved`, `moderation_notes`
- **Timestamps**: `created_at`, `updated_at`, `approved_at`
- **Metadata**: `helpful_votes`, `not_helpful_votes`, `report_count`

### RatingCategory
Rating category classification:
- **Category Info**: `category_id`, `name`, `description`, `weight`
- **Rating Type**: `rating_type`, `scale_min`, `scale_max`
- **Display**: `display_name`, `icon`, `sort_order`
- **Metadata**: `created_at`, `updated_at`

### RatingModeration
Review moderation and content filtering:
- **Moderation Info**: `rating_id`, `moderator_id`, `moderation_status`
- **Content Analysis**: `sentiment_score`, `content_flags`, `language`
- **Actions**: `moderation_actions`, `moderation_notes`
- **Timestamps**: `moderated_at`, `created_at`

### RatingAnalytics
Rating analytics and insights:
- **Analytics Info**: `product_id`, `period`, `total_ratings`
- **Metrics**: `average_rating`, `rating_distribution`, `review_count`
- **Trends**: `rating_trend`, `sentiment_trend`, `volume_trend`
- **Metadata**: `calculated_at`, `created_at`



## Repository Layer

The `RatingRepositoryRepository` class provides data access operations for the Rating module using the Repository pattern.

### Key Features
- **Base Repository**: Extends `BaseRepository[Rating]` for common CRUD operations
- **Advanced Filtering**: Complex filtering, sorting, and pagination
- **Relationship Loading**: Eager loading of related entities
- **Type Safety**: Generic type support for better IDE support
- **Error Handling**: Consistent error handling across all operations

### Repository Methods

#### Basic CRUD Operations
- `get_by_id(entity_id)` - Get entity by ID
- `create(entity_data)` - Create new entity
- `update(entity_id, entity_data)` - Update existing entity
- `delete(entity_id)` - Delete entity
- `get_all(limit, offset)` - Get all entities with pagination

#### Advanced Query Methods
- `get_ratings_with_details(rating_id)` - Rating with all related details
- `get_ratings_by_product(product_id)` - Ratings by product
- `get_ratings_by_user(user_id)` - Ratings by user
- `get_ratings_by_score(score)` - Ratings by score
- `get_ratings_by_score_range(min_score, max_score)` - Ratings by score range
- `get_high_ratings(min_score)` - High ratings
- `get_low_ratings(max_score)` - Low ratings
- `get_average_rating_by_product(product_id)` - Average rating for product
- `get_rating_count_by_product(product_id)` - Rating count for product
- `get_rating_distribution_by_product(product_id)` - Rating distribution
- `get_recent_ratings(limit)` - Recent ratings
- `get_top_rated_products(limit, min_ratings)` - Top rated products
- `get_user_rating_for_product(user_id, product_id)` - User rating for product
- `update_rating(rating_id, new_score, new_comment)` - Update rating

#### Statistics and Analytics
- `get_rating_statistics()` - Statistics for dashboard/reporting

### Usage Example

```python
from app.rating.repository import RatingRepositoryRepository

# Initialize repository
rating_repo = RatingRepositoryRepository()

# Get entity by ID
entity = rating_repo.get_by_id("entity-uuid")

# Get entities with filtering
filter_obj = FilterObj()
result = rating_repo.get_paginated(filter_obj)

# Create new entity
new_entity = rating_repo.create(entity_data)

# Update entity
rating_repo.update("entity-uuid", update_data)

# Get statistics
stats = rating_repo.get_rating_statistics()
```


## API Endpoints

### Rating Management
- `GET /ratings` - List ratings with filtering
- `GET /ratings/{id}` - Get rating details
- `POST /ratings` - Create new rating
- `PUT /ratings/{id}` - Update rating
- `DELETE /ratings/{id}` - Delete rating
- `POST /ratings/{id}/report` - Report inappropriate rating

### Product Ratings
- `GET /products/{id}/ratings` - Get product ratings
- `GET /products/{id}/ratings/summary` - Get rating summary
- `GET /products/{id}/ratings/analytics` - Get rating analytics
- `POST /products/{id}/ratings` - Rate product
- `GET /products/{id}/ratings/trends` - Get rating trends

### Review Management
- `GET /ratings/{id}/reviews` - Get rating reviews
- `POST /ratings/{id}/reviews` - Add review to rating
- `PUT /ratings/{id}/reviews/{review_id}` - Update review
- `DELETE /ratings/{id}/reviews/{review_id}` - Delete review
- `POST /ratings/{id}/reviews/{review_id}/helpful` - Mark review as helpful

### Rating Moderation
- `GET /ratings/moderation/pending` - Get pending ratings for moderation
- `GET /ratings/moderation/{id}` - Get moderation details
- `POST /ratings/moderation/{id}/approve` - Approve rating
- `POST /ratings/moderation/{id}/reject` - Reject rating
- `POST /ratings/moderation/{id}/flag` - Flag rating for review

### Rating Analytics
- `GET /ratings/analytics/overview` - Get rating overview
- `GET /ratings/analytics/trends` - Get rating trends
- `GET /ratings/analytics/sentiment` - Get sentiment analysis
- `GET /ratings/analytics/products` - Get product rating analytics
- `GET /ratings/analytics/customers` - Get customer rating analytics

### Rating Categories
- `GET /ratings/categories` - List rating categories
- `GET /ratings/categories/{id}` - Get category details
- `POST /ratings/categories` - Create category
- `PUT /ratings/categories/{id}` - Update category
- `DELETE /ratings/categories/{id}` - Delete category

## Business Logic

### Rating Creation
1. **Order Validation**: Verify customer has purchased the product
2. **Rating Validation**: Validate rating value and format
3. **Content Filtering**: Filter inappropriate content
4. **Duplicate Check**: Prevent duplicate ratings
5. **Moderation Queue**: Add to moderation queue if required
6. **Notification**: Notify relevant parties
7. **Analytics Update**: Update rating analytics

### Review Moderation
1. **Content Analysis**: Analyze review content for appropriateness
2. **Sentiment Analysis**: Analyze review sentiment
3. **Flag Detection**: Detect flagged content and spam
4. **Manual Review**: Route for manual review if needed
5. **Approval Process**: Approve or reject reviews
6. **Feedback Loop**: Provide feedback to moderators

### Rating Aggregation
1. **Score Calculation**: Calculate average rating scores
2. **Distribution Analysis**: Analyze rating distribution
3. **Trend Analysis**: Track rating trends over time
4. **Sentiment Tracking**: Track sentiment changes
5. **Volume Analysis**: Analyze rating volume patterns
6. **Insight Generation**: Generate rating insights

### Recommendation Engine
1. **Rating-based Filtering**: Filter products by rating
2. **Similarity Analysis**: Find similar products based on ratings
3. **Customer Matching**: Match customers with similar preferences
4. **Trend Analysis**: Identify trending products
5. **Personalization**: Personalize recommendations
6. **A/B Testing**: Test recommendation algorithms

## Validation Schemas

### RatingCreateSchema
```python
{
    "customer_id": "uuid (required)",
    "product_id": "uuid (required)",
    "order_id": "uuid (required)",
    "rating_value": "integer (required, min 1, max 5)",
    "rating_type": "string (required, enum: product|service|delivery|overall)",
    "rating_category": "string (optional, max 100 chars)",
    "review_title": "string (optional, max 200 chars)",
    "review_text": "string (optional, max 2000 chars)",
    "is_verified_purchase": "boolean (optional, default true)"
}
```

### RatingUpdateSchema
```python
{
    "rating_value": "integer (optional, min 1, max 5)",
    "review_title": "string (optional, max 200 chars)",
    "review_text": "string (optional, max 2000 chars)",
    "rating_category": "string (optional, max 100 chars)"
}
```

### RatingModerationSchema
```python
{
    "rating_id": "uuid (required)",
    "moderation_status": "string (required, enum: pending|approved|rejected|flagged)",
    "moderation_notes": "string (optional, max 1000 chars)",
    "moderation_actions": "array of strings (optional)",
    "content_flags": "array of strings (optional)"
}
```

### RatingAnalyticsSchema
```python
{
    "product_id": "uuid (optional)",
    "period": "string (required, enum: daily|weekly|monthly|yearly)",
    "start_date": "date (optional)",
    "end_date": "date (optional)",
    "include_sentiment": "boolean (optional, default true)",
    "include_trends": "boolean (optional, default true)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When rating not found
- **BusinessLogicException**: For business rule violations
- **ModerationException**: For moderation-related errors
- **AnalyticsException**: For analytics processing errors

## Dependencies

- **Product Module**: For product information
- **Order Module**: For order validation
- **User Module**: For customer information
- **Notification Module**: For rating notifications
- **Analytics Module**: For rating analytics
- **Content Filtering**: For content moderation

## Usage Examples

### Creating a Rating
```python
from app.rating.service import RatingService
from app.rating.schemas import RatingCreateSchema

service = RatingService()
rating_data = {
    "customer_id": "customer-uuid",
    "product_id": "product-uuid",
    "order_id": "order-uuid",
    "rating_value": 5,
    "rating_type": "product",
    "rating_category": "quality",
    "review_title": "Excellent 3D printed phone case",
    "review_text": "The quality is amazing and the print is very detailed. Highly recommended!",
    "is_verified_purchase": True
}

rating = service.create_rating(rating_data)
```

### Managing Reviews
```python
# Get product ratings
ratings = service.get_product_ratings(product_id, page=1, per_page=20)

# Get rating summary
summary = service.get_rating_summary(product_id)

# Update rating
service.update_rating(rating_id, {
    "rating_value": 4,
    "review_text": "Updated review text"
})

# Report inappropriate rating
service.report_rating(rating_id, "inappropriate_content")
```

### Rating Moderation
```python
# Get pending ratings for moderation
pending_ratings = service.get_pending_moderation()

# Moderate rating
moderation_data = {
    "rating_id": "rating-uuid",
    "moderation_status": "approved",
    "moderation_notes": "Content is appropriate",
    "moderation_actions": ["approved"],
    "content_flags": []
}

service.moderate_rating(moderation_data)

# Flag rating for review
service.flag_rating(rating_id, "spam_suspected")
```

### Rating Analytics
```python
# Get rating analytics
analytics = service.get_rating_analytics({
    "product_id": "product-uuid",
    "period": "monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "include_sentiment": True,
    "include_trends": True
})

# Get rating trends
trends = service.get_rating_trends(product_id, period="monthly")

# Get sentiment analysis
sentiment = service.get_sentiment_analysis(product_id)
```

### Rating Categories
```python
# Create rating category
category_data = {
    "name": "print_quality",
    "description": "Quality of 3D printing",
    "weight": 0.3,
    "rating_type": "product",
    "scale_min": 1,
    "scale_max": 5,
    "display_name": "Print Quality",
    "icon": "quality_icon.svg"
}

category = service.create_rating_category(category_data)

# Get rating categories
categories = service.get_rating_categories()
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache rating summaries and analytics
- **Aggregation**: Efficient rating aggregation algorithms
- **Background Processing**: Process analytics in background
- **CDN Integration**: Cache rating data for fast delivery

## Security

- **Content Moderation**: Filter inappropriate content
- **Spam Prevention**: Prevent spam ratings and reviews
- **Access Control**: Role-based permissions for moderation
- **Data Validation**: Validate all rating inputs
- **Audit Logging**: Log all rating operations

## Integration Points

- **Product Catalog**: Product information and display
- **Order Management**: Order validation for verified purchases
- **Customer Management**: Customer information and preferences
- **Analytics Platform**: Rating analytics and insights
- **Content Moderation**: Automated content filtering
- **Recommendation Engine**: Rating-based recommendations

## Future Enhancements

- **AI-Powered Moderation**: Machine learning content moderation
- **Sentiment Analysis**: Advanced sentiment analysis
- **Visual Reviews**: Support for image and video reviews
- **Social Integration**: Social media integration for reviews
- **Gamification**: Rating and review gamification
- **Advanced Analytics**: Predictive rating analytics