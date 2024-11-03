from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_crate_profile_receiver(sender, instance, created, **kwargs):
    if created:
        print("Create the user profile")
        UserProfile.objects.create(user=instance)
        print("User profile is created")
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            # Crea el UserProfile si no existe
            UserProfile.objects.create(user=instance)
            print("Profile did not exist, but I created one")
        print("User is updated")

@receiver(pre_save, sender=User)
def pre_save_profile_receiver(sender, instance, **kwards):
    print(instance.username, "This user is being saved")
