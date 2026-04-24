import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import yaml from 'js-yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const ROOT_DIR = path.join(__dirname, '../..');

// Robust YAML parser using js-yaml
function parseYaml(content) {
  try {
    return yaml.load(content) || {};
  } catch (error) {
    console.warn('⚠️  Warning: failed to parse YAML:', error.message);
    return {};
  }
}

// Read config to get site title and description
function getSiteConfig() {
  const configPath = path.join(ROOT_DIR, '_config.yml');
  const content = fs.readFileSync(configPath, 'utf8');
  return parseYaml(content);
}

function getMdFiles(dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (fs.statSync(full).isDirectory()) {
      results.push(...getMdFiles(full));
    } else if (entry.endsWith('.md') && entry !== 'README.md') {
      results.push(full);
    }
  }
  return results;
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
    const filePaths = getMdFiles(categoryDir);

    for (const filePath of filePaths) {
      const file = path.basename(filePath);
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

      const relDir = path.relative(categoryDir, path.dirname(filePath));

      articles.push({
        title: frontMatter.title || slug,
        excerpt: frontMatter.excerpt || '',
        category: category,
        relDir,
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
  const titleLines = wrapText(articleTitle, 32);
  const excerptLines = wrapText(excerpt, 60);
  const maxExcerptLines = Math.min(3, Math.max(1, 5 - titleLines.length));

  let yPos = 100;

  let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="630" fill="#ffffff"/>
  <text x="60" y="${yPos}" font-size="64" font-weight="600" fill="#1b1f23" font-family="Georgia, serif">${escapeXml(siteTitle)}</text>
  <text x="60" y="${yPos + 45}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">${escapeXml(siteDescription)}</text>
  <line x1="60" y1="${yPos + 70}" x2="1050" y2="${yPos + 70}" stroke="#e6e8eb" stroke-width="1"/>`;

  yPos += 150;

  titleLines.forEach((line, idx) => {
    svg += `\n  <text x="60" y="${yPos + idx * 64}" font-size="52" font-weight="700" fill="#1b1f23" font-family="Georgia, serif">${escapeXml(line)}</text>`;
  });

  yPos += titleLines.length * 64 + 10;

  excerptLines.slice(0, maxExcerptLines).forEach((line, idx) => {
    svg += `\n  <text x="60" y="${yPos + idx * 48}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">${escapeXml(line)}</text>`;
  });

  yPos += excerptLines.slice(0, maxExcerptLines).length * 48 + 25;

  svg += `\n  <line x1="60" y1="${yPos}" x2="1050" y2="${yPos}" stroke="#e6e8eb" stroke-width="1"/>
  <text x="1050" y="${yPos + 45}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif" text-anchor="end">${escapeXml(domain)}</text>
</svg>`;

  return svg;
}

// Generate SVG for OG image - Homepage (no title/excerpt, larger header)
function generateSVGHomepage(siteTitle, siteDescription, domain, authorName) {
  const descLines = wrapText(siteDescription, 48);

  let yPos = 180;

  let svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="630" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="630" fill="#ffffff"/>
  <text x="60" y="${yPos}" font-size="100" font-weight="600" fill="#1b1f23" font-family="Georgia, serif">${escapeXml(siteTitle)}</text>`;

  yPos += 90;

  descLines.forEach((line, idx) => {
    svg += `\n  <text x="60" y="${yPos + idx * 46}" font-size="36" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">${escapeXml(line)}</text>`;
  });

  yPos += descLines.length * 46 + 20;

  svg += `\n  <line x1="60" y1="${yPos}" x2="1050" y2="${yPos}" stroke="#e6e8eb" stroke-width="1"/>`;
  yPos += 50;

  svg += `\n  <text x="60" y="${yPos}" font-size="28" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">Published occasionally. Written for clarity over volume.</text>
  <line x1="60" y1="540" x2="1050" y2="540" stroke="#e6e8eb" stroke-width="1"/>
  <text x="60" y="584" font-size="24" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif">Written and maintained by ${escapeXml(authorName)}</text>
  <text x="1050" y="584" font-size="24" fill="#5b636a" font-family="system-ui, -apple-system, sans-serif" text-anchor="end">${escapeXml(domain)}</text>
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
    const domain = siteConfig.url ? siteConfig.url.replace(/^https?:\/\//, '') : '';
    const authorName = siteConfig.author?.name || '';

    // Generate homepage OG image
    const homepageOutputPath = path.join(ROOT_DIR, 'assets/og-images', 'homepage.png');
    const homepageDir = path.dirname(homepageOutputPath);
    fs.mkdirSync(homepageDir, { recursive: true });
    const homepageSvg = generateSVGHomepage(
      siteConfig.title,
      siteConfig.description,
      domain,
      authorName
    );
    const homepageBuffer = Buffer.from(homepageSvg);
    await sharp(homepageBuffer).webp({ quality: 85 }).toFile(homepageOutputPath.replace('.png', '.webp'));
    console.log(`✓ Generated homepage.webp`);

    // Generate article OG images
    for (const article of articles) {
      const ogDir = path.join(ROOT_DIR, 'assets/og-images', article.category, article.relDir);

      fs.mkdirSync(ogDir, { recursive: true });

      const outputPath = path.join(ogDir, `${article.slug}.png`);
      const svgString = generateSVG(
        siteConfig.title || 'Insight Notes',
        siteConfig.description || 'Notes',
        article.title,
        article.excerpt,
        domain
      );

      const svgBuffer = Buffer.from(svgString);
      await sharp(svgBuffer).webp({ quality: 85 }).toFile(outputPath.replace('.png', '.webp'));

      const relPath = [article.category, article.relDir, `${article.slug}.webp`].filter(Boolean).join('/');
      console.log(`✓ Generated ${relPath}`);
    }

    console.log('\n✨ All OG images generated successfully!');
  } catch (error) {
    console.error('Error generating OG images:', error);
    process.exit(1);
  }
}

// Run
generateImages();
