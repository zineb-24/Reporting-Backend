from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    id_user = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    admin_creator = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_users'
    )
    
    # Required for AbstractBaseUser
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    # Required functions for Django Admin Panel, ensures superusers have all permissions
    def has_perm(self, perm, obj=None):  
        return self.is_superuser

    def has_module_perms(self, app_label):  
        return self.is_superuser


class Salle(models.Model):
    id_salle = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    date_creation = models.DateTimeField(default=timezone.now)
    admin_creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='created_salles',
        limit_choices_to={'is_admin': True}
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Salle'
        verbose_name_plural = 'Salles'


class User_Salle(models.Model):
    id = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='salle_Links'
    )
    id_salle = models.ForeignKey(
        Salle,
        on_delete=models.CASCADE,
        related_name='user_Links'
    )
    date_creation = models.DateTimeField(default=timezone.now)
    admin_creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_Links',
        limit_choices_to={'is_admin': True}
    )
    
    def __str__(self):
        return f"{self.id_user.name} linked to {self.id_salle.name}"
    
    class Meta:
        verbose_name = 'User-Salle Links'
        verbose_name_plural = 'User-Salle Links'
        # Prevent duplicate links
        unique_together = ('id_user', 'id_salle')


class Reglement(models.Model):
    id_reglement = models.AutoField(primary_key=True)
    num_contrat = models.CharField(max_length=100)
    id_client = models.CharField(max_length=100)
    date_contrat = models.DateField()
    date_debut = models.DateField()
    date_fin = models.DateField()
    categorie = models.CharField(max_length=100)
    agent = models.CharField(max_length=100)
    tarif = models.DecimalField(max_digits=10, decimal_places=2)
    date_assurance = models.DateField()
    date_reglement = models.DateField()
    montant_reglement = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=50)
    id_salle = models.ForeignKey('Salle', on_delete=models.CASCADE)

    def __str__(self):
        return f"Contrat {self.num_contrat} - Client {self.id_client}"
