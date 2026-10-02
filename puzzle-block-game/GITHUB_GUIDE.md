# GitHub Upload Guide

This guide will help you upload your Puzzle Block Game to GitHub.

## Step 1: Create a GitHub Account

1. Go to [github.com](https://github.com)
2. Click "Sign up" and create your account
3. Verify your email address

## Step 2: Create a New Repository

1. After logging in, click the **+** icon in the top-right corner
2. Select **"New repository"**
3. Fill in the repository details:
   - **Repository name**: `puzzle-block-game`
   - **Description**: `A classic Tetris-style puzzle game built with Python and Tkinter`
   - **Public/Private**: Choose **Public** (recommended for sharing)
   - **Initialize with README**: ❌ Uncheck (we have our own)
   - **Add .gitignore**: Select **Python**
   - **Choose license**: Select **MIT License**
4. Click **"Create repository"**

## Step 3: Prepare Your Local Project

Open your terminal/command prompt and navigate to your project folder:

```bash
cd C:\Users\ADMIN\.devin\puzzle-block-game
```

## Step 4: Initialize Git

```bash
git init
```

## Step 5: Add Files to Git

```bash
git add .
```

## Step 6: Make Your First Commit

```bash
git commit -m "Initial commit: Puzzle Block Game"
```

## Step 7: Connect to GitHub Repository

Copy the repository URL from GitHub (choose HTTPS for simplicity):
```
https://github.com/YOUR_USERNAME/puzzle-block-game.git
```

Then run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/puzzle-block-game.git
```

## Step 8: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub username and password (or personal access token).

## Step 9: Add Screenshots (Important!)

Before pushing or after pushing, add screenshots:

1. Run the game: `python puzzle_block_game.py`
2. Take screenshots using your OS screenshot tool:
   - **Windows**: Win + Shift + S
   - **Mac**: Cmd + Shift + 4
3. Save screenshots to the `screenshots/` folder:
   - `demo.png` - Main demo image
   - `gameplay.png` - Active gameplay
   - `gameover.png` - Game over screen
4. Commit and push the screenshots:
   ```bash
   git add screenshots/
   git commit -m "Add game screenshots"
   git push
   ```

## Step 10: Update README.md

Edit the README.md file to personalize it:

1. Replace `yourusername` with your actual GitHub username
2. Update the author information
3. Add your contact email
4. Update the demo link when you have one
5. Add real screenshots (replace the placeholder links)

## Step 11: Create a Demo Link (Optional)

### Option A: GitHub Pages (Free Hosting)

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under **Source**, select **main** branch
4. Click **Save**
5. Your site will be available at: `https://YOUR_USERNAME.github.io/puzzle-block-game/`

### Option B: Record a Demo Video

1. Use screen recording software:
   - **Windows**: Xbox Game Bar (Win + G)
   - **Mac**: QuickTime Player
   - **OBS Studio** (free, cross-platform)
2. Record a short gameplay demo (30-60 seconds)
3. Upload to YouTube
4. Add the YouTube link to your README.md

### Option C: GIF Animation

1. Use a tool to create animated GIFs:
   - **LICEcap** (free, lightweight)
   - **ScreenToGif** (Windows)
   - **Gifski** (Mac)
2. Record gameplay as GIF
3. Upload the GIF to your repository
4. Embed it in README.md:
   ```markdown
   ![Game Demo](screenshots/demo.gif)
   ```

## Step 12: Add Topics/Tags

1. Go to your repository on GitHub
2. Click **Settings** → **Topics**
3. Add relevant tags:
   - `python`
   - `game`
   - `tetris`
   - `tkinter`
   - `puzzle`
   - `pygame-alternative`

## Step 13: Create a Release (Optional)

1. Go to your repository
2. Click **Releases** → **"Create a new release"**
3. Tag version: `v1.0.0`
4. Release title: `First Release`
5. Description: Add release notes
6. Click **"Publish release"**

## Maintenance Tips

### Regular Updates

When you make changes to the game:

```bash
git add .
git commit -m "Describe your changes"
git push
```

### Creating Issues

If you find bugs or want to track features:
1. Go to **Issues** tab
2. Click **"New issue"**
3. Describe the bug or feature request

### Branching for Features

For larger changes:

```bash
git checkout -b feature-name
# Make changes
git add .
git commit -m "Add feature"
git push origin feature-name
# Then create a Pull Request on GitHub
```

## Project Structure After Upload

Your GitHub repository should look like this:

```
puzzle-block-game/
├── puzzle_block_game.py
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── CONTRIBUTING.md
├── GITHUB_GUIDE.md
└── screenshots/
    ├── README.md
    ├── demo.png          # Add these
    ├── gameplay.png      # Add these
    └── gameover.png      # Add these
```

## Share Your Project

Once uploaded, share your project:
- Post on social media (Twitter, Reddit, LinkedIn)
- Share in Python communities
- Add to your portfolio
- Submit to game development forums

## Troubleshooting

### Authentication Issues

If you get authentication errors:
1. Create a Personal Access Token on GitHub
   - Settings → Developer settings → Personal access tokens
2. Use the token instead of your password
3. Or use SSH keys for authentication

### Push Rejected

If push is rejected:
```bash
git pull origin main --rebase
git push origin main
```

### Large Files

If files are too large:
- Use `git lfs` for large files
- Or compress images before adding

---

**Congratulations! Your game is now on GitHub! 🎉**
