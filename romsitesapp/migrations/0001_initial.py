from django.db import migrations, models
import django.core.validators


SEED_REVIEWS = [
    {
        "name": "Sarah Miller",
        "rating": 5,
        "comment": "Romsites delivered our landscaping layout and invoice system incredibly fast. Our clients love the simplicity. Highly recommend for any Indiana business seeking custom development!",
    },
    {
        "name": "Marcus Thompson",
        "rating": 5,
        "comment": "Exceptional local SEO services! Our Indianapolis tree care business tripled its inbound calls within months. A absolute game changer for our operations.",
    },
    {
        "name": "David Garret",
        "rating": 5,
        "comment": "Their database architecture and customer portals are top tier. They optimized our laggy legacy system, speeding up loading times by nearly 400%.",
    },
]


def seed_reviews(apps, schema_editor):
    Review = apps.get_model("romsitesapp", "Review")
    for entry in SEED_REVIEWS:
        Review.objects.create(
            name=entry["name"],
            rating=entry["rating"],
            comment=entry["comment"],
            is_approved=True,
        )


def remove_seed_reviews(apps, schema_editor):
    Review = apps.get_model("romsitesapp", "Review")
    Review.objects.filter(name__in=[r["name"] for r in SEED_REVIEWS]).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                (
                    "rating",
                    models.IntegerField(
                        default=5,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                    ),
                ),
                ("comment", models.TextField(max_length=2000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_approved", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        # Bring over the existing reviews.json content so nothing is lost in
        # the move from file-based storage to the database (see audit: the
        # old data/reviews.json approach didn't survive restarts on Render's
        # ephemeral filesystem).
        migrations.RunPython(seed_reviews, remove_seed_reviews),
    ]
