#!/bin/bash

# Claude Code Update Script
# Fixes auto-update failures by performing clean reinstallation

set -e  # Exit on any error

echo "🔄 Claude Code Update Script"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists npm; then
    print_error "npm is not installed. Please install Node.js and npm first."
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

print_success "Prerequisites check passed"
echo ""

# Get current version if Claude is installed
if command_exists claude; then
    CURRENT_VERSION=$(claude --version 2>/dev/null || echo "Unknown")
    print_status "Current Claude Code version: $CURRENT_VERSION"
else
    print_status "Claude Code not currently installed"
    CURRENT_VERSION="Not installed"
fi
echo ""

# Step 1: Check Node.js and npm versions
print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"
echo ""

# Step 2: Find Claude Code installation directory
print_status "Locating Claude Code installation..."

# Try to find the installation path
if command_exists npm; then
    NPM_ROOT=$(npm root -g 2>/dev/null || echo "")
    if [ -n "$NPM_ROOT" ]; then
        CLAUDE_DIR="$NPM_ROOT/@anthropic-ai/claude-code"
        print_status "Expected Claude Code directory: $CLAUDE_DIR"
    else
        print_warning "Could not determine npm global root"
    fi
fi

# Step 3: Attempt normal uninstall first
print_status "Attempting graceful uninstall..."
if npm uninstall -g @anthropic-ai/claude-code >/dev/null 2>&1; then
    print_success "Graceful uninstall completed"
else
    print_warning "Graceful uninstall failed (this is expected if directory is corrupted)"
fi
echo ""

# Step 4: Force remove directory if it exists
if [ -n "$CLAUDE_DIR" ] && [ -d "$CLAUDE_DIR" ]; then
    print_status "Removing corrupted Claude Code directory..."
    if rm -rf "$CLAUDE_DIR" 2>/dev/null; then
        print_success "Directory removed successfully"
    else
        print_error "Failed to remove directory. You may need to run with sudo:"
        print_error "sudo rm -rf \"$CLAUDE_DIR\""
        echo ""
        print_status "Continuing anyway..."
    fi
else
    print_status "No existing directory found to remove"
fi
echo ""

# Step 5: Clear npm cache (helps with installation issues)
print_status "Clearing npm cache..."
if npm cache clean --force >/dev/null 2>&1; then
    print_success "npm cache cleared"
else
    print_warning "Failed to clear npm cache"
fi
echo ""

# Step 6: Install latest version
print_status "Installing latest Claude Code version..."
echo "This may take a moment..."

if npm install -g @anthropic-ai/claude-code; then
    print_success "Claude Code installation completed!"
else
    print_error "Installation failed. Trying alternative approach..."
    
    # Alternative: Install specific version
    print_status "Attempting to install latest stable version..."
    if npm install -g @anthropic-ai/claude-code@latest; then
        print_success "Alternative installation succeeded!"
    else
        print_error "All installation attempts failed."
        print_error "Manual steps:"
        print_error "1. Check your npm permissions"
        print_error "2. Try: npm install -g @anthropic-ai/claude-code --force"
        print_error "3. Or run this script with sudo (not recommended)"
        exit 1
    fi
fi
echo ""

# Step 7: Verify installation
print_status "Verifying installation..."

if command_exists claude; then
    NEW_VERSION=$(claude --version 2>/dev/null || echo "Unknown")
    print_success "Claude Code is now available"
    print_success "New version: $NEW_VERSION"
    
    if [ "$CURRENT_VERSION" != "$NEW_VERSION" ]; then
        print_success "✅ Update successful! ($CURRENT_VERSION → $NEW_VERSION)"
    else
        print_success "✅ Installation verified (same version)"
    fi
else
    print_error "Claude Code command not found after installation"
    print_error "You may need to:"
    print_error "1. Restart your terminal"
    print_error "2. Check your PATH includes npm global bin directory"
    exit 1
fi
echo ""

# Step 8: Test basic functionality
print_status "Testing basic functionality..."
if claude --help >/dev/null 2>&1; then
    print_success "Claude Code help command works"
else
    print_warning "Claude Code help command failed (may need terminal restart)"
fi

# Step 9: Check for updates
print_status "Checking if updates are available..."
UPDATE_CHECK=$(claude update 2>&1 || echo "Update check failed")
echo "$UPDATE_CHECK"
echo ""

# Final summary
echo "🎉 CLAUDE CODE UPDATE COMPLETE!"
echo "================================"
echo ""
print_success "Installation Summary:"
print_success "• Previous version: $CURRENT_VERSION"
print_success "• Current version: $NEW_VERSION"
print_success "• Status: Ready to use"
echo ""

print_status "Usage Tips:"
echo "• Run 'claude --version' to check version"
echo "• Run 'claude --help' for command options"  
echo "• Run 'claude update' to check for future updates"
echo "• If you see 'command not found', restart your terminal"
echo ""

print_status "Script completed successfully! ✅"