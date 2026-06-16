import express from "express";
import path from "path";
import fs from "fs";
import nunjucks from "nunjucks";

// Initializing the server app
const app = express();
const PORT = 3000;

// URL encoding parser & JSON parse support
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Serve static files from the '/static' folder
app.use("/static", express.static(path.join(process.cwd(), "static")));

// Custom Nunjucks Loader with direct Django-to-Nunjucks pre-compilation mappings
class DjangoNunjucksLoader extends nunjucks.FileSystemLoader {
  getSource(name: string): any {
    const result = super.getSource(name);
    if (result && result.src) {
      let source = result.src;

      // 1. Remove {% load static %} and other templates packages loads
      source = source.replace(/\{%\s*load\s+[^%]+\s*%\}/g, "");

      // 2. Convert {% static 'path' %} and {% static "path" %} into '/static/path'
      source = source.replace(/\{%\s*static\s+['"]([^'"]+)['"]\s*%\}/g, "/static/$1");

      // 3. Map {% url 'name' %} to standard route paths
      source = source.replace(/\{%\s*url\s+['"]home['"]\s*%\}/g, "/");
      source = source.replace(/\{%\s*url\s+['"]about['"]\s*%\}/g, "/about");
      source = source.replace(/\{%\s*url\s+['"]portfolio['"]\s*%\}/g, "/portfolio");
      source = source.replace(/\{%\s*url\s+['"]services['"]\s*%\}/g, "/services");
      source = source.replace(/\{%\s*url\s+['"]design['"]\s*%\}/g, "/design");
      source = source.replace(/\{%\s*url\s+['"]development['"]\s*%\}/g, "/development");
      source = source.replace(/\{%\s*url\s+['"]maintenance['"]\s*%\}/g, "/maintenance");
      source = source.replace(/\{%\s*url\s+['"]seo['"]\s*%\}/g, "/seo");

      // 4. Map {% csrf_token %} to clean dummy HTML input tag
      source = source.replace(/\{%\s*csrf_token\s*%\}/g, `<input type="hidden" name="csrfmiddlewaretoken" value="dummy_csrf_token_value">`);

      // 5. Replace legacy reviews.0 dot index representation with Nunjucks standard bracket index
      source = source.replace(/reviews\.0\./g, "reviews[0].");
      source = source.replace(/reviews\.0/g, "reviews[0]");

      // 6. Map Django loop indicators: counter index map
      source = source.replace(/forloop\.counter/g, "loop.index");

      result.src = source;
    }
    return result;
  }
}

// Initializing the preprocessor environment
const customLoader = new DjangoNunjucksLoader("templates", { noCache: true });
const env = new nunjucks.Environment(customLoader, { autoescape: true });

// Load local database reviewers
function getReviews(): any[] {
  const dbPath = path.join(process.cwd(), "data", "reviews.json");
  if (!fs.existsSync(dbPath)) {
    return [];
  }
  try {
    const data = fs.readFileSync(dbPath, "utf-8");
    return JSON.parse(data);
  } catch (err) {
    console.error("Database read error:", err);
    return [];
  }
}

// Write local database lists
function saveReviews(reviews: any[]) {
  const dataDir = path.join(process.cwd(), "data");
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  const dbPath = path.join(dataDir, "reviews.json");
  fs.writeFileSync(dbPath, JSON.stringify(reviews, null, 2), "utf-8");
}

// Form markup structure for about.html page
const form_html = `
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
    <textarea name="comment" id="id_comment" required placeholder="Describe your experience collaborating with ROMSITES Indiana dev lab..." rows="4" class="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-white text-xs font-semibold focus:border-amber-500/60 focus:ring-1 focus:ring-amber-500 outline-none transition-all resize-none"></textarea>
  </div>
</div>
`;

// Helper page render function
function renderDjango(res: any, templateName: string, context: any) {
  try {
    const rendered = env.render(templateName, {
      ...context,
      csrfmiddlewaretoken: "dummy_csrf_token_value"
    });
    res.send(rendered);
  } catch (err: any) {
    console.error("Rendering error for:", templateName, err);
    res.status(500).send(`Precompilation View Error: ${err.message}`);
  }
}

// ROUTE 1: Home View Page
app.get("/", (req, res) => {
  const reviews = getReviews();
  renderDjango(res, "index.html", { reviews });
});

// ROUTE 2: About View Page (displays form + newest review)
app.get("/about", (req, res) => {
  const reviews = getReviews();
  renderDjango(res, "about.html", { 
    reviews, 
    form_html,
    form_action: "/about"
  });
});

// ROUTE 2 POST: Submit Review
app.post("/about", (req, res) => {
  const { name, rating, comment } = req.body;
  if (!name || !rating || !comment) {
    return res.status(400).send("Validation Failure: Missing fields.");
  }
  
  const reviews = getReviews();
  const newReview = {
    id: (reviews.length + 1).toString(),
    name: name.toString().trim(),
    rating: parseInt(rating),
    comment: comment.toString().trim()
  };
  
  reviews.unshift(newReview); // Put on top
  saveReviews(reviews);
  
  res.redirect("/portfolio");
});

// ROUTE 3: Portfolio View Page (displays projects + all reviews with CRUD delete)
app.get("/portfolio", (req, res) => {
  const reviews = getReviews();
  renderDjango(res, "portfolio.html", { reviews });
});

// ROUTE 4: Core Services Solutions Map (with interactive pricing calculator)
app.get("/services", (req, res) => {
  renderDjango(res, "services.html", {});
});

// ROUTE 5: Web Design Details Page
app.get("/design", (req, res) => {
  renderDjango(res, "design.html", {});
});

// ROUTE 6: Web Development Details Page
app.get("/development", (req, res) => {
  renderDjango(res, "development.html", {});
});

// ROUTE 7: Website Maintenance details Page
app.get("/maintenance", (req, res) => {
  renderDjango(res, "maintenance.html", {});
});

// ROUTE 8: SEO Optimization details Page
app.get("/seo", (req, res) => {
  renderDjango(res, "seo.html", {});
});

// ROUTE 9: Confirm Delete Review Page GET
app.get("/delete-review/:id", (req, res) => {
  const { id } = req.params;
  const reviews = getReviews();
  const review = reviews.find(r => r.id === id);
  if (!review) {
    return res.redirect("/portfolio");
  }
  renderDjango(res, "delete_review.html", { review });
});

// ROUTE 9 POST: Perform Deletion
app.post("/delete-review/:id", (req, res) => {
  const { id } = req.params;
  let reviews = getReviews();
  reviews = reviews.filter(r => r.id !== id);
  saveReviews(reviews);
  res.redirect("/portfolio");
});

// Start Express server on specified Port and bind to host
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server actively running on port ${PORT}`);
});
