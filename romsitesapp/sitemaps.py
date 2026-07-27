from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Simple sitemap for the site's static (non-database-driven) pages."""
    protocol = 'https'

    def items(self):
        return [
            ('home', 1.0, 'weekly'),
            ('about', 0.6, 'monthly'),
            ('portfolio', 0.8, 'weekly'),
            ('services', 0.9, 'monthly'),
            ('design', 0.7, 'monthly'),
            ('development', 0.7, 'monthly'),
            ('maintenance', 0.7, 'monthly'),
            ('seo', 0.7, 'monthly'),
        ]

    def location(self, item):
        name, _, _ = item
        return reverse(name)

    def priority(self, item):
        _, priority, _ = item
        return priority

    def changefreq(self, item):
        _, _, freq = item
        return freq
