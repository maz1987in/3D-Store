# Favorite Module

The Favorite module manages user favorites, wishlists, and saved items in the 3D Store application, providing comprehensive favorite management capabilities.

## Overview

This module handles:
- User favorites and wishlist management
- Product and service favoriting
- Favorite organization and categorization
- Favorite sharing and collaboration
- Favorite analytics and insights
- Recommendation based on favorites
- Favorite notifications and updates

## Module Structure

```
favorite/
├── __init__.py          # Module initialization
├── model.py            # SQLAlchemy models
├── routes.py           # Flask API endpoints
├── service.py          # Business logic layer
├── swagger.yaml        # API documentation
└── README.md           # This documentation
```

## Models

### Favorite
Main favorite entity with the following key attributes:
- **Basic Info**: `favorite_id`, `user_id`, `item_id`, `item_type`
- **Item Details**: `item_name`, `item_description`, `item_image_url`
- **Organization**: `category_id`, `tags`, `notes`, `priority`
- **Status**: `is_active`, `is_public`, `is_shared`
- **Timestamps**: `created_at`, `updated_at`, `last_accessed`
- **Metadata**: `access_count`, `share_count`

### FavoriteCategory
Favorite categorization and organization:
- **Category Info**: `category_id`, `name`, `description`, `color`
- **Settings**: `is_default`, `is_public`, `sort_order`
- **User**: `user_id`, `is_system_category`
- **Metadata**: `created_at`, `updated_at`

### FavoriteTag
Favorite tagging and classification:
- **Tag Info**: `tag_id`, `name`, `description`, `color`
- **Usage**: `usage_count`, `is_active`
- **User**: `user_id`, `is_system_tag`
- **Metadata**: `created_at`, `updated_at`

### FavoriteShare
Favorite sharing and collaboration:
- **Share Info**: `share_id`, `favorite_id`, `shared_with`, `share_type`
- **Permissions**: `permissions`, `access_level`
- **Settings**: `expires_at`, `password_protected`, `password`
- **Status**: `is_active`, `created_by`
- **Metadata**: `created_at`, `updated_at`

### FavoriteAnalytics
Favorite analytics and insights:
- **Analytics Info**: `user_id`, `period`, `total_favorites`, `new_favorites`
- **Metrics**: `most_favorited`, `favorite_trends`, `category_distribution`
- **Behavior**: `favorite_patterns`, `access_patterns`
- **Metadata**: `calculated_at`, `created_at`

### FavoriteRecommendation
Favorite-based recommendations:
- **Recommendation Info**: `user_id`, `item_id`, `item_type`, `recommendation_type`
- **Score**: `recommendation_score`, `confidence_level`
- **Reason**: `recommendation_reason`, `similar_items`
- **Status**: `is_active`, `is_viewed`, `is_clicked`
- **Metadata**: `created_at`, `updated_at`

## API Endpoints

### Favorite Management
- `GET /favorites` - List user favorites
- `GET /favorites/{id}` - Get favorite details
- `POST /favorites` - Add item to favorites
- `PUT /favorites/{id}` - Update favorite
- `DELETE /favorites/{id}` - Remove from favorites
- `POST /favorites/{id}/toggle` - Toggle favorite status

### Favorite Categories
- `GET /favorites/categories` - List favorite categories
- `GET /favorites/categories/{id}` - Get category details
- `POST /favorites/categories` - Create category
- `PUT /favorites/categories/{id}` - Update category
- `DELETE /favorites/categories/{id}` - Delete category
- `GET /favorites/categories/{id}/favorites` - Get favorites in category

### Favorite Tags
- `GET /favorites/tags` - List favorite tags
- `GET /favorites/tags/{id}` - Get tag details
- `POST /favorites/tags` - Create tag
- `PUT /favorites/tags/{id}` - Update tag
- `DELETE /favorites/tags/{id}` - Delete tag
- `GET /favorites/tags/{id}/favorites` - Get favorites with tag

### Favorite Sharing
- `GET /favorites/{id}/shares` - List favorite shares
- `POST /favorites/{id}/shares` - Share favorite
- `PUT /favorites/{id}/shares/{share_id}` - Update share
- `DELETE /favorites/{id}/shares/{share_id}` - Revoke share
- `GET /favorites/shared/{token}` - Access shared favorite

### Favorite Search
- `GET /favorites/search` - Search favorites
- `GET /favorites/search/suggestions` - Get search suggestions
- `GET /favorites/filter` - Filter favorites
- `GET /favorites/sort` - Sort favorites

### Favorite Analytics
- `GET /favorites/analytics/overview` - Get favorite overview
- `GET /favorites/analytics/trends` - Get favorite trends
- `GET /favorites/analytics/categories` - Get category analytics
- `GET /favorites/analytics/popular` - Get popular favorites
- `GET /favorites/reports` - Generate favorite reports

### Favorite Recommendations
- `GET /favorites/recommendations` - Get recommendations
- `GET /favorites/recommendations/similar` - Get similar items
- `POST /favorites/recommendations/feedback` - Submit recommendation feedback
- `GET /favorites/recommendations/trending` - Get trending items

## Business Logic

### Favorite Management
1. **Item Favoriting**: Add items to user favorites
2. **Favorite Organization**: Organize favorites by categories and tags
3. **Favorite Updates**: Update favorite information and notes
4. **Favorite Removal**: Remove items from favorites
5. **Favorite Status**: Track favorite status and activity
6. **Favorite Validation**: Validate favorite items and availability

### Favorite Organization
1. **Category Management**: Create and manage favorite categories
2. **Tag Management**: Create and manage favorite tags
3. **Sorting and Filtering**: Sort and filter favorites
4. **Search Functionality**: Search within favorites
5. **Bulk Operations**: Perform bulk operations on favorites
6. **Import/Export**: Import and export favorite lists

### Favorite Sharing
1. **Share Creation**: Create shareable favorite lists
2. **Permission Management**: Manage sharing permissions
3. **Access Control**: Control access to shared favorites
4. **Collaboration**: Enable collaborative favorite management
5. **Privacy Settings**: Manage privacy and visibility settings
6. **Share Analytics**: Track sharing activity and engagement

### Favorite Analytics
1. **Usage Tracking**: Track favorite usage and patterns
2. **Trend Analysis**: Analyze favorite trends and patterns
3. **Category Analytics**: Analyze favorite categories
4. **User Behavior**: Analyze user favorite behavior
5. **Insight Generation**: Generate insights from favorite data
6. **Reporting**: Create comprehensive favorite reports

### Favorite Recommendations
1. **Recommendation Engine**: Generate item recommendations
2. **Similar Items**: Find similar items based on favorites
3. **Trending Items**: Identify trending items
4. **Personalization**: Personalize recommendations
5. **Feedback Loop**: Collect and use recommendation feedback
6. **Performance Tracking**: Track recommendation performance

## Validation Schemas

### FavoriteCreateSchema
```python
{
    "user_id": "uuid (required)",
    "item_id": "uuid (required)",
    "item_type": "string (required, enum: product|service|design|project)",
    "item_name": "string (required, max 255 chars)",
    "item_description": "string (optional, max 1000 chars)",
    "item_image_url": "string (optional, valid URL)",
    "category_id": "uuid (optional)",
    "tags": "array of strings (optional)",
    "notes": "string (optional, max 1000 chars)",
    "priority": "string (optional, enum: low|medium|high)",
    "is_public": "boolean (optional, default false)",
    "is_shared": "boolean (optional, default false)"
}
```

### FavoriteUpdateSchema
```python
{
    "item_name": "string (optional, max 255 chars)",
    "item_description": "string (optional, max 1000 chars)",
    "item_image_url": "string (optional, valid URL)",
    "category_id": "uuid (optional)",
    "tags": "array of strings (optional)",
    "notes": "string (optional, max 1000 chars)",
    "priority": "string (optional, enum: low|medium|high)",
    "is_public": "boolean (optional)",
    "is_shared": "boolean (optional)"
}
```

### FavoriteCategoryCreateSchema
```python
{
    "name": "string (required, max 255 chars)",
    "description": "string (optional, max 1000 chars)",
    "color": "string (optional, hex color)",
    "is_default": "boolean (optional, default false)",
    "is_public": "boolean (optional, default false)",
    "sort_order": "integer (optional, default 0)"
}
```

### FavoriteTagCreateSchema
```python
{
    "name": "string (required, max 100 chars, unique)",
    "description": "string (optional, max 500 chars)",
    "color": "string (optional, hex color)",
    "is_active": "boolean (optional, default true)"
}
```

### FavoriteShareCreateSchema
```python
{
    "favorite_id": "uuid (required)",
    "shared_with": "string (required, email or user_id)",
    "share_type": "string (required, enum: view|edit|admin)",
    "permissions": "array of strings (optional)",
    "access_level": "string (required, enum: private|team|public)",
    "expires_at": "datetime (optional)",
    "password_protected": "boolean (optional, default false)",
    "password": "string (optional, min 6 chars)"
}
```

## Error Handling

The module uses comprehensive error handling:
- **ValidationException**: For input validation errors
- **ResourceNotFoundException**: When favorite not found
- **BusinessLogicException**: For business rule violations
- **PermissionException**: For permission-related errors
- **ShareException**: For sharing-related errors

## Dependencies

- **User Module**: For user authentication and management
- **Product Module**: For product information
- **Service Module**: For service information
- **Analytics Module**: For favorite analytics
- **Notification Module**: For favorite notifications
- **Recommendation Engine**: For item recommendations

## Usage Examples

### Managing Favorites
```python
from app.favorite.service import FavoriteService
from app.favorite.schemas import FavoriteCreateSchema

service = FavoriteService()
favorite_data = {
    "user_id": "user-uuid",
    "item_id": "product-uuid",
    "item_type": "product",
    "item_name": "Custom Phone Case",
    "item_description": "3D printed custom phone case with logo",
    "item_image_url": "https://example.com/images/phone-case.jpg",
    "category_id": "category-uuid",
    "tags": ["phone", "case", "custom", "3d-printed"],
    "notes": "Great design, want to order in different colors",
    "priority": "high",
    "is_public": False,
    "is_shared": False
}

favorite = service.create_favorite(favorite_data)
```

### Managing Favorite Categories
```python
# Create favorite category
category_data = {
    "name": "3D Printing Projects",
    "description": "Favorites related to 3D printing projects",
    "color": "#007bff",
    "is_default": False,
    "is_public": True,
    "sort_order": 1
}

category = service.create_favorite_category(category_data)

# Get favorites in category
favorites = service.get_favorites_in_category(category_id)

# Update category
service.update_favorite_category(category_id, {
    "name": "3D Printing & Design",
    "description": "Updated description",
    "color": "#28a745"
})
```

### Managing Favorite Tags
```python
# Create favorite tag
tag_data = {
    "name": "beginner-friendly",
    "description": "Items suitable for beginners",
    "color": "#ffc107",
    "is_active": True
}

tag = service.create_favorite_tag(tag_data)

# Get favorites with tag
favorites = service.get_favorites_with_tag(tag_id)

# Update tag
service.update_favorite_tag(tag_id, {
    "description": "Updated description for beginner-friendly items",
    "color": "#17a2b8"
})
```

### Favorite Sharing
```python
# Share favorite
share_data = {
    "favorite_id": "favorite-uuid",
    "shared_with": "friend@example.com",
    "share_type": "view",
    "permissions": ["view", "comment"],
    "access_level": "team",
    "expires_at": "2024-12-31T23:59:59Z",
    "password_protected": False
}

share = service.share_favorite(share_data)

# Update share settings
service.update_favorite_share(favorite_id, share_id, {
    "share_type": "edit",
    "permissions": ["view", "edit", "comment"]
})

# Revoke share
service.revoke_favorite_share(favorite_id, share_id)
```

### Favorite Search and Filtering
```python
# Search favorites
search_results = service.search_favorites(
    query="phone case",
    category_filter="3d-printing",
    tag_filter=["custom", "beginner-friendly"],
    sort_by="created_at",
    sort_order="desc",
    limit=20
)

# Filter favorites
filtered_favorites = service.filter_favorites(
    category_id="category-uuid",
    tags=["phone", "case"],
    priority="high",
    is_public=True
)

# Sort favorites
sorted_favorites = service.sort_favorites(
    favorites=favorites,
    sort_by="priority",
    sort_order="desc"
)
```

### Favorite Analytics
```python
# Get favorite overview
overview = service.get_favorite_overview(user_id)

# Get favorite trends
trends = service.get_favorite_trends(
    user_id=user_id,
    period="monthly"
)

# Get category analytics
category_analytics = service.get_category_analytics(user_id)

# Get popular favorites
popular_favorites = service.get_popular_favorites(limit=10)

# Generate favorite report
report = service.generate_favorite_report(
    user_id=user_id,
    report_type="usage",
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### Favorite Recommendations
```python
# Get recommendations
recommendations = service.get_recommendations(
    user_id=user_id,
    limit=10,
    recommendation_type="similar"
)

# Get similar items
similar_items = service.get_similar_items(
    item_id="item-uuid",
    item_type="product",
    limit=5
)

# Get trending items
trending_items = service.get_trending_items(
    category_id="category-uuid",
    limit=10
)

# Submit recommendation feedback
feedback = service.submit_recommendation_feedback(
    user_id=user_id,
    item_id="item-uuid",
    feedback_type="helpful",
    rating=5
)
```

## Performance Considerations

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Cache frequently accessed favorites
- **Search Optimization**: Optimize search performance
- **Recommendation Caching**: Cache recommendation results
- **Analytics Processing**: Process analytics in background

## Security

- **Access Control**: Role-based permissions for favorite management
- **Privacy Settings**: Respect user privacy preferences
- **Share Security**: Secure favorite sharing
- **Data Validation**: Validate all favorite inputs
- **Audit Logging**: Log all favorite operations

## Integration Points

- **Product Catalog**: Product information and details
- **Service Catalog**: Service information and details
- **User Management**: User authentication and profiles
- **Analytics Platform**: Favorite analytics and insights
- **Recommendation Engine**: Item recommendation system
- **Notification System**: Favorite notifications and updates

## Future Enhancements

- **AI-Powered Recommendations**: Machine learning recommendations
- **Social Features**: Social favorite sharing and discovery
- **Collaborative Lists**: Collaborative favorite list management
- **Mobile App**: Mobile favorite management
- **Voice Interface**: Voice-activated favorite management
- **Advanced Analytics**: Advanced favorite analytics and insights
