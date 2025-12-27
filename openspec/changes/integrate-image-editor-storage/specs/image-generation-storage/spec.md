# Image Editor Storage Integration

## ADDED Requirements

### Requirement: Image Editor Authentication
The image editor page SHALL require user authentication to access.

#### Scenario: Authenticated user accesses image editor
- **GIVEN** a user is logged in
- **WHEN** they navigate to `/image`
- **THEN** the system displays the image editor interface
- **AND** loads their saved images from the database

#### Scenario: Unauthenticated user accesses image editor
- **GIVEN** a user is not logged in
- **WHEN** they navigate to `/image`
- **THEN** the system redirects to `/login?next=/image`

### Requirement: Save Generated Images to Database
The image editor SHALL automatically save generated images to the database using the existing user_images storage system.

#### Scenario: User generates image successfully
- **GIVEN** a user has generated an image via the image editor
- **WHEN** the generation completes successfully
- **THEN** the system automatically saves the image to database via `POST /api/v1/images`
- **AND** includes model name, prompt, image URL, and request/response metadata
- **AND** displays a success notification
- **AND** adds the image to the "生成存储库" section
- **AND** updates the user's storage quota

#### Scenario: Save fails due to storage quota exceeded
- **GIVEN** a user has generated an image
- **WHEN** saving would exceed their storage quota
- **THEN** the system displays HTTP 413 error message
- **AND** shows "存储空间不足" (Storage quota exceeded) notification
- **AND** does not add the image to the repository

#### Scenario: Save fails due to network error
- **GIVEN** a user has generated an image
- **WHEN** the API request fails
- **THEN** the system displays an error notification
- **AND** allows the user to retry the save operation

### Requirement: Display Saved Images from Database
The "生成存储库" section SHALL display images saved in the database, replacing the local Drawing History.

#### Scenario: User loads page with saved images
- **GIVEN** a user has previously saved images
- **WHEN** they load the image editor page
- **THEN** the system fetches images via `GET /api/v1/images?limit=50`
- **AND** displays images in a grid layout with thumbnails
- **AND** shows image metadata (title, model, prompt, created_at)
- **AND** orders images by creation date (newest first)

#### Scenario: User has no saved images
- **GIVEN** a user has not saved any images
- **WHEN** they load the image editor page
- **THEN** the "生成存储库" section displays an empty state message
- **AND** shows "暂无生成记录" (No generation records)

#### Scenario: Pagination for many images
- **GIVEN** a user has more than 50 saved images
- **WHEN** they scroll to the bottom of the repository
- **THEN** the system loads the next page via `GET /api/v1/images?limit=50&offset=50`
- **AND** appends additional images to the grid

### Requirement: Delete Images from Repository
Users SHALL be able to delete saved images from the repository.

#### Scenario: User deletes an image
- **GIVEN** a user is viewing their saved images
- **WHEN** they click the delete button on an image
- **THEN** the system displays a confirmation dialog "确定要删除这条记录吗？"
- **WHEN** the user confirms
- **THEN** the system calls `DELETE /api/v1/images/{image_id}`
- **AND** removes the image from the grid on success
- **AND** updates the user's storage quota
- **AND** displays a success notification

#### Scenario: User cancels deletion
- **GIVEN** a user clicks delete on an image
- **WHEN** the confirmation dialog appears
- **AND** the user clicks cancel
- **THEN** the system does not delete the image
- **AND** closes the dialog

### Requirement: Navigation to Home Page
The image editor SHALL provide a button to return to the home page.

#### Scenario: User clicks back to home button
- **GIVEN** a user is on the image editor page
- **WHEN** they click the "返回主页面" button
- **THEN** the system navigates to `/` (home page)

### Requirement: CSRF Protection for API Calls
All API requests from the image editor SHALL include CSRF tokens when using cookie-based authentication.

#### Scenario: User makes API request with cookie auth
- **GIVEN** a user is authenticated via session cookie
- **WHEN** the image editor makes a non-GET API request
- **THEN** the system includes `X-CSRF-Token` header from `csrf_token` cookie
- **AND** the request succeeds if token matches

#### Scenario: CSRF token missing or invalid
- **GIVEN** a user is authenticated via session cookie
- **WHEN** the image editor makes a POST/DELETE request without CSRF token
- **THEN** the API returns HTTP 403 Forbidden
- **AND** the system displays an error notification

### Requirement: Integration with Storage Page
Images saved from the image editor SHALL appear in the main storage page at `/storage`.

#### Scenario: User views storage page after saving images
- **GIVEN** a user has saved images from the image editor
- **WHEN** they navigate to `/storage`
- **THEN** the system displays both videos and images in their respective sections
- **AND** images from the editor appear in the "Images" grid
- **AND** users can view, download, or delete images from this page
