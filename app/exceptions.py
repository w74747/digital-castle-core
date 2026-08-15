"""
Custom Exception Classes for Digital Castle S.P.C
---
Hierarchical exception structure for comprehensive error handling.
"""


class DigitalCastleException(Exception):
    """
    Base exception for all Digital Castle errors.
    All custom exceptions inherit from this.
    """

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.error_code}] {self.message}"

    def to_dict(self):
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# Configuration Errors
class ConfigError(DigitalCastleException):
    """
    Raised when environment configuration is missing or invalid.
    Examples: Missing API keys, invalid database URL, etc.
    """

    pass


class MissingCredentialsError(ConfigError):
    """Raised when API credentials are not found."""

    pass


# API & Network Errors
class APIError(DigitalCastleException):
    """
    Raised when an API call fails.
    Parent class for specific API errors.
    """

    pass


class APITimeoutError(APIError):
    """Raised when an API call times out."""

    pass


class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded (HTTP 429)."""

    pass


class APIAuthenticationError(APIError):
    """Raised when API authentication fails (HTTP 401)."""

    pass


class APIAuthorizationError(APIError):
    """Raised when API authorization fails (HTTP 403)."""

    pass


class APINotFoundError(APIError):
    """Raised when API resource is not found (HTTP 404)."""

    pass


class APIServerError(APIError):
    """Raised when API server returns 5xx error."""

    pass


class NetworkError(DigitalCastleException):
    """
    Raised when network communication fails.
    """

    pass


# Validation Errors
class ValidationError(DigitalCastleException):
    """
    Raised when input validation fails.
    Parent class for specific validation errors.
    """

    pass


class InvalidInputError(ValidationError):
    """Raised when input format is invalid."""

    pass


class MissingFieldError(ValidationError):
    """Raised when required field is missing."""

    pass


class InvalidTypeError(ValidationError):
    """Raised when field type is incorrect."""

    pass


# Rate Limiting
class RateLimitExceeded(DigitalCastleException):
    """
    Raised when request rate limit is exceeded.
    This can be application-level rate limiting.
    """

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


# Resource Errors
class ResourceNotFound(DigitalCastleException):
    """Raised when a resource is not found in the database."""

    pass


class ResourceAlreadyExists(DigitalCastleException):
    """Raised when attempting to create a resource that already exists."""

    pass


class ResourceDeleted(DigitalCastleException):
    """Raised when attempting to access a deleted resource."""

    pass


class InsufficientPermissions(DigitalCastleException):
    """Raised when user lacks required permissions."""

    pass


# Database Errors
class DatabaseError(DigitalCastleException):
    """
    Parent class for database-related errors.
    """

    pass


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""

    pass


class DatabaseQueryError(DatabaseError):
    """Raised when a database query fails."""

    pass


class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""

    pass


class MigrationError(DatabaseError):
    """Raised when a database migration fails."""

    pass


# Document Generation Errors
class DocumentGenerationError(DigitalCastleException):
    """
    Parent class for document generation errors.
    """

    pass


class TemplateNotFoundError(DocumentGenerationError):
    """Raised when template file is not found."""

    pass


class TemplateRenderError(DocumentGenerationError):
    """Raised when template rendering fails."""

    pass


class PDFGenerationError(DocumentGenerationError):
    """Raised when PDF generation fails."""

    pass


class InvalidDocumentDataError(DocumentGenerationError):
    """Raised when document data is invalid."""

    pass


# Security Errors
class SecurityError(DigitalCastleException):
    """
    Parent class for security-related errors.
    """

    pass


class InvalidTokenError(SecurityError):
    """Raised when JWT token is invalid or expired."""

    pass


class EncryptionError(SecurityError):
    """Raised when encryption/decryption fails."""

    pass


class SignatureVerificationError(SecurityError):
    """Raised when cryptographic signature verification fails."""

    pass


# Business Logic Errors
class BusinessLogicError(DigitalCastleException):
    """
    Parent class for business logic errors.
    """

    pass


class InvalidTaskStateError(BusinessLogicError):
    """Raised when task state transition is invalid."""

    pass


class InvoiceGenerationError(BusinessLogicError):
    """Raised when invoice generation fails."""

    pass


class SequenceNumberError(BusinessLogicError):
    """Raised when sequence number generation fails."""

    pass


# GitHub Integration Errors
class GitHubError(DigitalCastleException):
    """
    Parent class for GitHub-related errors.
    """

    pass


class GitHubConnectionError(GitHubError):
    """Raised when GitHub API connection fails."""

    pass


class GitHubAuthenticationError(GitHubError):
    """Raised when GitHub authentication fails."""

    pass


class RepositoryNotFoundError(GitHubError):
    """Raised when GitHub repository is not found."""

    pass


class BranchNotFoundError(GitHubError):
    """Raised when Git branch is not found."""

    pass


class PullRequestError(GitHubError):
    """Raised when pull request operation fails."""

    pass


# Telegram Errors
class TelegramError(DigitalCastleException):
    """
    Parent class for Telegram-related errors.
    """

    pass


class TelegramConnectionError(TelegramError):
    """Raised when Telegram connection fails."""

    pass


class TelegramAuthenticationError(TelegramError):
    """Raised when Telegram authentication fails."""

    pass


class TelegramMessageError(TelegramError):
    """Raised when message sending fails."""

    pass


# System Errors
class SystemError(DigitalCastleException):
    """
    Parent class for critical system errors.
    """

    pass


class InitializationError(SystemError):
    """Raised when system initialization fails."""

    pass


class ShutdownError(SystemError):
    """Raised when system shutdown fails."""

    pass


class HealthCheckError(SystemError):
    """Raised when health check fails."""

    pass


# Utility function for error handling
def get_error_response(exception: DigitalCastleException) -> dict:
    """
    Convert exception to standardized error response.
    """
    return {
        "success": False,
        "error": exception.to_dict(),
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
