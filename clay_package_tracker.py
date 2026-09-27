#!/usr/bin/env python3
"""
Clay Package Tracker - Track UPS, FedEx, USPS packages
https://github.com/robb99/clay-package-tracker

Usage:
    python3 clay_package_tracker.py add <tracking_number> [--carrier <ups|fedex|usps>]
    python3 clay_package_tracker.py list
    python3 clay_package_tracker.py check [tracking_number]
    python3 clay_package_tracker.py remove <tracking_number>
    python3 clay_package_tracker.py status [--json]
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

PACKAGE_DB = Path.home() / ".clay" / "packages.json"

# Ensure storage exists
PACKAGE_DB.parent.mkdir(parents=True, exist_ok=True)

def load_packages():
    """Load package database"""
    if PACKAGE_DB.exists():
        with open(PACKAGE_DB) as f:
            return json.load(f)
    return {"packages": []}

def save_packages(data):
    """Save package database"""
    with open(PACKAGE_DB, 'w') as f:
        json.dump(data, f, indent=2)

def detect_carrier(tracking_number):
    """Auto-detect carrier from tracking number format"""
    tn = tracking_number.replace(" ", "").upper()
    
    # UPS: 1Z999999999999999999
    if tn.startswith("1Z"):
        return "ups"
    # FedEx: 12-999-9999-999999999 or 999999999999
    elif tn.isdigit() and len(tn) == 12 or len(tn) == 15:
        return "fedex"
    # USPS: 22-999-9999-9999999999 or 94-999-9999-9999999999
    elif tn.replace("-", "").isdigit() and len(tn.replace("-", "")) >= 20:
        return "usps"
    # Default to UPS (most common)
    return "ups"

def add_package(tracking_number, carrier=None, description=None):
    """Add a package to track"""
    packages = load_packages()
    tn = tracking_number.strip()
    
    if carrier is None:
        carrier = detect_carrier(tn)
    
    # Check if already exists
    for pkg in packages["packages"]:
        if pkg["tracking_number"] == tn:
            print(f"Package {tn} already tracked!")
            return
    
    pkg = {
        "tracking_number": tn,
        "carrier": carrier,
        "description": description or f"Package from {carrier.upper()}",
        "added_at": datetime.now().isoformat(),
        "last_checked": None,
        "status": "unknown",
        "events": []
    }
    
    packages["packages"].append(pkg)
    save_packages(packages)
    print(f"✓ Added {tn} ({carrier.upper()}) - {pkg['description']}")

def list_packages():
    """List all tracked packages"""
    packages = load_packages()
    
    if not packages["packages"]:
        print("No packages tracked yet!")
        print("Usage: python3 clay_package_tracker.py add <tracking_number>")
        return
    
    print("\n📦 Tracked Packages")
    print("=" * 70)
    
    for pkg in packages["packages"]:
        status_emoji = {
            "delivered": "✅",
            "in_transit": "📦",
            "out_for_delivery": "🚚",
            "exception": "⚠️",
            "unknown": "❓"
        }.get(pkg.get("status", "unknown"), "❓")
        
        print(f"\n{status_emoji} {pkg['tracking_number']}")
        print(f"   Carrier: {pkg['carrier'].upper()}")
        print(f"   Description: {pkg['description']}")
        print(f"   Status: {pkg.get('status', 'unknown').replace('_', ' ').title()}")
        
        if pkg.get("last_checked"):
            print(f"   Last checked: {pkg['last_checked'][:19]}")
        
        if pkg.get("events") and len(pkg["events"]) > 0:
            latest = pkg["events"][0]
            print(f"   Latest: {latest.get('date', '')} - {latest.get('location', '')}")
            print(f"           {latest.get('description', '')}")

def check_package(tracking_number=None, json_output=False):
    """Check status of packages"""
    packages = load_packages()
    
    # Check specific or all
    if tracking_number:
        pkgs_to_check = [p for p in packages["packages"] if p["tracking_number"] == tracking_number]
    else:
        pkgs_to_check = packages["packages"]
    
    results = []
    
    for pkg in pkgs_to_check:
        # Simulate API check (in production, would use carrier APIs)
        # For now, we'll use a public tracking approach or mock
        result = {
            "tracking_number": pkg["tracking_number"],
            "carrier": pkg["carrier"],
            "status": "in_transit",  # Default
            "events": [],
            "checked_at": datetime.now().isoformat()
        }
        
        # Try to get real data (this is simplified - real impl would need API keys)
        try:
            if pkg["carrier"] == "ups":
                result["status"] = _check_ups(pkg["tracking_number"])
            elif pkg["carrier"] == "fedex":
                result["status"] = _check_fedex(pkg["tracking_number"])
            elif pkg["carrier"] == "usps":
                result["status"] = _check_usps(pkg["tracking_number"])
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        results.append(result)
        
        # Update stored package
        for stored in packages["packages"]:
            if stored["tracking_number"] == pkg["tracking_number"]:
                stored["last_checked"] = result["checked_at"]
                stored["status"] = result["status"]
                if result.get("events"):
                    stored["events"] = result["events"]
        
        if json_output:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n📦 {pkg['tracking_number']} ({pkg['carrier'].upper()})")
            print(f"   Status: {result['status'].replace('_', ' ').title()}")
    
    save_packages(packages)
    return results

def _check_ups(tracking_number):
    """Check UPS tracking - uses public tracking page scraping or API"""
    # Note: Real implementation would need UPS API or web scraping
    # For now, return placeholder - would integrate with actual API
    return "in_transit"

def _check_fedex(tracking_number):
    """Check FedEx tracking"""
    return "in_transit"

def _check_usps(tracking_number):
    """Check USPS tracking"""
    return "in_transit"

def remove_package(tracking_number):
    """Remove a package from tracking"""
    packages = load_packages()
    original_count = len(packages["packages"])
    
    packages["packages"] = [p for p in packages["packages"] if p["tracking_number"] != tracking_number]
    
    if len(packages["packages"]) < original_count:
        save_packages(packages)
        print(f"✓ Removed {tracking_number}")
    else:
        print(f"Package {tracking_number} not found")

def notify_delivery(pkg):
    """Send notification when package is delivered"""
    # Use clay_voice to announce
    msg = f"Package delivered! {pkg['description']}"
    
    try:
        subprocess.run([
            "python3", 
            str(Path(__file__).parent.parent / "tools" / "clay_voice.py"),
            msg
        ], check=True, capture_output=True)
    except Exception as e:
        print(f"Voice notification failed: {e}")
    
    # Also try clay-notify
    try:
        subprocess.run([
            "python3",
            str(Path(__file__).parent.parent / "projects" / "clay-notify" / "clay_notify.py"),
            "Package Delivered",
            pkg['description']
        ], check=True, capture_output=True)
    except Exception as e:
        print(f"Desktop notification failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Clay Package Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add package
    add_parser = subparsers.add_parser("add", help="Add a package to track")
    add_parser.add_argument("tracking_number", help="Tracking number")
    add_parser.add_argument("--carrier", choices=["ups", "fedex", "usps"], help="Carrier")
    add_parser.add_argument("--desc", "--description", dest="description", help="Description")
    
    # List packages
    subparsers.add_parser("list", help="List all tracked packages")
    
    # Check status
    check_parser = subparsers.add_parser("check", help="Check package status")
    check_parser.add_argument("tracking_number", nargs="?", help="Specific tracking number")
    check_parser.add_argument("--json", action="store_true", help="JSON output")
    
    # Remove package
    remove_parser = subparsers.add_parser("remove", help="Remove a package")
    remove_parser.add_argument("tracking_number", help="Tracking number")
    
    # Status summary
    subparsers.add_parser("status", help="Quick status summary")
    
    args = parser.parse_args()
    
    if args.command == "add":
        add_package(args.tracking_number, args.carrier, args.description)
    elif args.command == "list":
        list_packages()
    elif args.command == "check":
        check_package(args.tracking_number, args.json)
    elif args.command == "remove":
        remove_package(args.tracking_number)
    elif args.command == "status":
        packages = load_packages()
        delivered = sum(1 for p in packages["packages"] if p.get("status") == "delivered")
        in_transit = sum(1 for p in packages["packages"] if p.get("status") == "in_transit")
        
        if args.json:
            print(json.dumps({
                "total": len(packages["packages"]),
                "delivered": delivered,
                "in_transit": in_transit
            }))
        else:
            print(f"📦 Package Summary: {len(packages["packages"])} total, {delivered} delivered, {in_transit} in transit")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
