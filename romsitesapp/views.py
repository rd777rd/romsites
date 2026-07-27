import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Review

# Minimum seconds a visitor must spend on the review form before a submission
# is accepted. Bots that fetch-and-POST immediately are rejected; this needs
# no external service and no extra dependency.
MIN_FORM_FILL_SECONDS = 3

FORM_HTML = """
<div class="space-y-4 text-left">
  <div>
    <label for="id_name" class="block text-xs font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">Your Name</label>
    <input type="text" name="name" id="id_name" required placeholder="Sarah Miller" class="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500 outline-none transition-all">
  </div>
  <div>
    <label for="id_rating" class="block text-xs font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">Rating Score</label>
    <select name="rating" id="id_rating" required class="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 text-xs font-bold focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500 outline-none transition-all cursor-pointer">
      <option value="5">★★★★★ (5 Stars - Outstanding)</option>
      <option value="4">★★★★☆ (4 Stars - Excellent)</option>
      <option value="3">★★★☆☆ (3 Stars - Satisfied)</option>
      <option value="2">★★☆☆☆ (2 Stars - Needs Improvement)</option>
      <option value="1">★☆☆☆☆ (1 Star - Poor)</option>
    </select>
  </div>
  <div>
    <label for="id_comment" class="block text-xs font-extrabold uppercase text-slate-400 mb-1.5 tracking-wider">Detailed Feedback Comment</label>
    <textarea name="comment" id="id_comment" required placeholder="Describe your experience collaborating with ROMSITES..." rows="4" class="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500 outline-none transition-all resize-none"></textarea>
  </div>
  <div style="position:absolute; left:-9999px; width:1px; height:1px; overflow:hidden;" aria-hidden="true">
    <label for="id_website">Leave this field blank</label>
    <input type="text" name="website" id="id_website" tabindex="-1" autocomplete="off">
  </div>
  <input type="hidden" name="form_started_at" value="{form_started_at}">
</div>
"""


def _approved_reviews():
    return Review.objects.filter(is_approved=True)


def home_view(request):
    reviews = _approved_reviews()
    return render(request, 'index.html', {'reviews': reviews})


def about_view(request):
    reviews = _approved_reviews()
    form_html = FORM_HTML.format(form_started_at=time.time())

    if request.method == 'POST':
        # Honeypot: hidden field real visitors never fill in.
        if request.POST.get('website'):
            return redirect('portfolio')

        # Reject submissions faster than a human could plausibly type a review.
        try:
            started_at = float(request.POST.get('form_started_at', 0))
        except (TypeError, ValueError):
            started_at = 0
        if started_at and (time.time() - started_at) < MIN_FORM_FILL_SECONDS:
            return redirect('portfolio')

        name = (request.POST.get('name') or '').strip()
        comment = (request.POST.get('comment') or '').strip()
        try:
            rating = int(request.POST.get('rating', 5))
        except (TypeError, ValueError):
            rating = 5
        rating = min(5, max(1, rating))

        if name and comment:
            Review.objects.create(
                name=name[:255],
                rating=rating,
                comment=comment[:2000],
                is_approved=False,  # held for staff review before publishing
            )
            return redirect('portfolio')

    return render(request, 'about.html', {
        'reviews': reviews,
        'form_html': form_html,
        'form_action': '/about'
    })


def portfolio_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        reviews = Review.objects.all()
    else:
        reviews = _approved_reviews()
    return render(request, 'portfolio.html', {'reviews': reviews})


def services_view(request):
    return render(request, 'services.html')


def design_view(request):
    return render(request, 'design.html')


def development_view(request):
    return render(request, 'development.html')


def maintenance_view(request):
    return render(request, 'maintenance.html')


def seo_view(request):
    return render(request, 'seo.html')


def delete_review_view(request, review_id):
    is_admin = request.user.is_authenticated and request.user.is_staff

    # Gate on admin status before rendering anything -- previously this page
    # showed the review content and a "delete" confirmation UI to anonymous
    # visitors on GET, only blocking the actual delete action on POST.
    if not is_admin:
        return redirect('portfolio')

    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        review.delete()
        return redirect('portfolio')

    return render(request, 'delete_review.html', {
        'review': review,
        'is_admin': True,
    })


def approve_review_view(request, review_id):
    if not (request.user.is_authenticated and request.user.is_staff):
        return redirect('portfolio')
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.is_approved = True
        review.save(update_fields=['is_approved'])
        messages.success(request, f"Review from {review.name} is now published.")
    return redirect('portfolio')
