import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ROOT_DIR = path.join(__dirname, '../..');

// Simple YAML parser for top-level keys
function parseYaml(content) {
  const result = {};
  const lines = content.split('\n');
  for (const line of lines) {
    if (line.startsWith('title:')) {
      result.title = line.replace('title:', '').trim().replace(/^["']|["']$/g, '');
    }
    if (line.startsWith('description:')) {
      result.description = line.replace('description:', '').trim().replace(/^["']|["']$/g, '');
    }
    if (line.startsWith('excerpt:')) {
      result.excerpt = line.replace('excerpt:', '').trim().replace(/^["']|["']$/g, '');
    }
    if (line.startsWith('permalink:')) {
      result.permalink = line.replace('permalink:', '').trim().replace(/^["']|["']$/g, '');
    }
    if (line.startsWith('category:')) {
      result.category = line.replace('category:', '').trim().replace(/^["']|["']$/g, '');
    }
  }
  return result;
}

// Read config to get site title and description
function getSiteConfig() {
  const configPath = path.join(ROOT_DIR, '_config.yml');
  const content = fs.readFileSync(configPath, 'utf8');
  return parseYaml(content);
}

// Read all markdown files from src/
function getArticles() {
  const articles = [];
  const srcDir = path.join(ROOT_DIR, 'src');

  const categories = fs.readdirSync(srcDir).filter(f => 
    fs.statSync(path.join(srcDir, f)).isDirectory()
  );

  for (const categoryName of categories) {
    const categoryDir = path.join(srcDir, categoryName);
    const files = fs.readdirSync(categoryDir).filter(f => f.endsWith('.md') && f !== 'README.md');

    for (const file of files) {
      const filePath = path.join(categoryDir, file);
      const content = fs.readFileSync(filePath, 'utf8');

      // Extract front matter
      const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
      if (!frontMatterMatch) continue;

      const frontMatter = parseYaml(frontMatterMatch[1]);
      // Extract slug from permalink or filename
      let slug, category;
      if (frontMatter.permalink) {
        // permalink: /digital-health/single-source-truth-no-tech-problem/ -> extract parts
        const parts = frontMatter.permalink.split('/').filter(p => p.length > 0);
        category = parts[0];
        slug = parts[1];
      } else {
        slug = file.replace('.md', '');
        // Remove leading number-dash pattern like Jekyll does (e.g. "1-name" -> "name")
        slug = slug.replace(/^\d+-/, '');
        category = frontMatter.category || categoryName;
      }

      articles.push({
        title: frontMatter.title || slug,
        excerpt: frontMatter.excerpt || '',
        category: category,
        slug,
        path: `/${frontMatter.category || category}/${slug}/`
      });
    }
  }

  return articles;
}

// Wrap text to fit width
function wrapText(text, maxLineLength) {
  const lines = [];
  let currentLine = '';
  const words = text.split(' ');
  
  for (const word of words) {
    if ((currentLine + ' ' + word).length > maxLineLength) {
      if (currentLine) lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = currentLine ? currentLine + ' ' + word : word;
    }
  }
  if (currentLine) lines.push(currentLine);
  
  return lines;
}

// Generate SVG for OG image - Article
function generateSVG(siteTitle, siteDescription, articleTitle, excerpt, domain) {
  // Wrap texts - more aggressive wrapping for title
  const titleLines = wrapText(articleTitle, 38);
  const excerptLines = wrapText(excerpt, 85);
  
  // Build SVG with proper layout
  let yPos = 100;
  
  // Site header section
  let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <!-- White background -->
  <rect width="1200" height="630" fill="#ffffff"/>
  
  <!-- Site header section -->
  <!-- Site title -->
  <text x="60" y="${yPos}" font-size="64" font-weight="600" fill="#1b1f23" font-family="Georgia, serif">${escapeXml(siteTitle)}</text>
  
  <!-- Site description -->
  <text x="60" y="${yPos + 45}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">${escapeXml(siteDescription)}</text>
  
  <!-- Top separator line -->
  <line x1="60" y1="${yPos + 70}" x2="1140" y2="${yPos + 70}" stroke="#e6e8eb" stroke-width="1"/>
  
  <!-- Article title section -->`;
  
  yPos += 150;
  
  // Article title (smaller, wrappable)
  titleLines.forEach((line, idx) => {
    svg += `\n  <text x="60" y="${yPos + (idx * 68)}" font-size="52" font-weight="700" fill="#1b1f23" font-family="Georgia, serif">${escapeXml(line)}</text>`;
  });
  
  yPos += titleLines.length * 68 + 10;
  
  // Excerpt section (larger, full width)
  excerptLines.slice(0, 3).forEach((line, idx) => {
    svg += `\n  <text x="60" y="${yPos + (idx * 52)}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">${escapeXml(line)}</text>`;
  });
  
  // Update yPos for bottom separator
  yPos += excerptLines.slice(0, 3).length * 52 + 25;
  
  // Bottom separator line
  svg += `\n  <line x1="60" y1="${yPos}" x2="1140" y2="${yPos}" stroke="#e6e8eb" stroke-width="1"/>
  
  <!-- Domain footer (bottom right) -->
  <text x="1080" y="${yPos + 45}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif" text-anchor="end">${escapeXml(domain)}</text>
</svg>`;
  
  return svg;
}

// Generate SVG for OG image - Homepage (no title/excerpt, larger header)
function generateSVGHomepage(siteTitle, siteDescription, domain) {
  let yPos = 200;
  
  let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <!-- White background -->
  <rect width="1200" height="630" fill="#ffffff"/>
  
  <!-- Site header section (larger) -->
  <!-- Site title -->
  <text x="60" y="${yPos}" font-size="100" font-weight="600" fill="#1b1f23" font-family="Georgia, serif">${escapeXml(siteTitle)}</text>
  
  <!-- Site description -->
  <text x="60" y="${yPos + 80}" font-size="42" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">${escapeXml(siteDescription)}</text>
  
  <!-- Top separator line -->
  <line x1="60" y1="${yPos + 124}" x2="1140" y2="${yPos + 124}" stroke="#e6e8eb" stroke-width="1"/>
  
  <!-- Tagline -->
  <text x="60" y="${yPos + 170}" font-size="32" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">Published occasionally. Written for clarity over volume.</text>
  
  <!-- Bottom separator line -->
  <line x1="60" y1="550" x2="1140" y2="550" stroke="#e6e8eb" stroke-width="1"/>
  
  <!-- Author footer (bottom left) -->
  <text x="60" y="595" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">Written and maintained by Alessandro Saglia</text>
  
  <!-- Domain footer (bottom right) -->
  <text x="1080" y="595" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif" text-anchor="end">${escapeXml(domain)}</text>
</svg>`;
  
  return svg;
}

function escapeXml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function generateImages() {
  try {
    const siteConfig = getSiteConfig();
    const articles = getArticles();
    
    console.log(`Found ${articles.length} articles. Generating OG images...`);
    console.log(`Site config - Title: "${siteConfig.title}", Description: "${siteConfig.description}"`);
    
    // Extract domain from URL
    const domain = siteConfig.url ? siteConfig.url.replace(/^https?:\/\//, '') : 'insight.ale-saglia.com';

    // Generate homepage OG image
    const homepageOutputPath = path.join(ROOT_DIR, 'assets/og-images', 'homepage.png');
    const homepageDir = path.dirname(homepageOutputPath);
    if (!fs.existsSync(homepageDir)) {
      fs.mkdirSync(homepageDir, { recursive: true });
    }
    const homepageSvg = generateSVGHomepage(
      siteConfig.title,
      siteConfig.description,
      domain
    );
    await sharp(Buffer.from(homepageSvg))
      .png()
      .toFile(homepageOutputPath);
    console.log(`✓ Generated homepage.png`);

    // Generate article OG images
    for (const article of articles) {
      const ogDir = path.join(ROOT_DIR, 'assets/og-images', article.category);
      
      // Create directory if it doesn't exist
      if (!fs.existsSync(ogDir)) {
        fs.mkdirSync(ogDir, { recursive: true });
      }

      const outputPath = path.join(ogDir, `${article.slug}.png`);
      const svgString = generateSVG(
        siteConfig.title || 'Insight Notes',
        siteConfig.description || 'Notes',
        article.title,
        article.excerpt,
        domain
      );
      
      // Convert SVG to PNG using sharp
      await sharp(Buffer.from(svgString))
        .png()
        .toFile(outputPath);

      console.log(`✓ Generated ${article.category}/${article.slug}.png`);
    }

    console.log('\n✨ All OG images generated successfully!');
  } catch (error) {
    console.error('Error generating OG images:', error);
    process.exit(1);
  }
}

// Run
generateImages();
