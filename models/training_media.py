from django.db import models
from django.core.validators import FileExtensionValidator
from .training import TrainingSession
from .user import User


class TrainingSessionMedia(models.Model):
    """
    Stores media files (images) for training sessions.
    Each session can have up to 4 images.
    """

    # Links to training session
    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name='media_files'
    )

    # Image file with validation
    image = models.ImageField(
        upload_to='training_sessions/%Y/%m/%d/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    # File metadata
    file_size = models.IntegerField(null=True, blank=True)  # in bytes
    file_name = models.CharField(max_length=255, null=True, blank=True)

    # Audit fields
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_training_media'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'models_training_session_media'
        ordering = ['-uploaded_at']
        verbose_name = 'Training Session Media'
        verbose_name_plural = 'Training Session Media'

    def __str__(self):
        return f"Media for session {self.session_id} - {self.file_name}"

    def save(self, *args, **kwargs):
        # Auto-calculate file size before saving
        if self.image:
            self.file_size = self.image.size
            self.file_name = self.image.name
        super().save(*args, **kwargs)
