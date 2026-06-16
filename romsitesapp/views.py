import json
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404

REVIEWS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reviews.json')

def get_reviews():
    if not os.path.exists(REVIEWS_FILE):
        return []
    try:
        with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_reviews(reviews):
    os.makedirs(os.path.dirname(REVIEWS_FILE), exist_ok=True)
    try:
        with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def home_view(request):
    reviews = get_reviews()
    return render(request, 'index.html', {'reviews': reviews})

def about_view(request):
    reviews = get_reviews()
    
    form_html = """
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
</div>
"""
    if request.method == 'POST':
        name = request.POST.get('name')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if name and rating and comment:
            reviews = get_reviews()
            new_review = {
                'id': str(len(reviews) + 1),
                'name': name.strip(),
                'rating': int(rating),
                'comment': comment.strip()
            }
            reviews.insert(0, new_review)
            save_reviews(reviews)
            return redirect('portfolio')
            
    return render(request, 'about.html', {
        'reviews': reviews,
        'form_html': form_html,
        'form_action': '/about'
    })

def portfolio_view(request):
    reviews = get_reviews()
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
    reviews = get_reviews()
    review = next((r for r in reviews if r['id'] == str(review_id)), None)
    if not review:
        return redirect('portfolio')
        
    if request.method == 'POST':
        reviews = [r for r in reviews if r['id'] != str(review_id)]
        save_reviews(reviews)
        return redirect('portfolio')
        
    return render(request, 'delete_review.html', {'review': review})
