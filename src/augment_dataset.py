import json
import os
from pathlib import Path
import logging

def load_pilot_dataset():
    """
    Load pilot dataset from JSON file for validation and training
    
    Returns:
        list: List of pilot dataset items with ticket content and expected categories
    """
    dataset_path = Path("data/pilot_dataset_augmented.json")
    
    if not dataset_path.exists():
        logging.warning(f"Pilot dataset not found at {dataset_path}")
        return create_default_pilot_dataset()
    
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logging.info(f"Loaded {len(data)} items from pilot dataset")
        return data
    
    except Exception as e:
        logging.error(f"Error loading pilot dataset: {e}")
        return create_default_pilot_dataset()

def create_default_pilot_dataset():
    """
    Create a default pilot dataset for testing when none exists
    
    Returns:
        list: Default pilot dataset
    """
    default_dataset = [
        {
            "ticket_id": "PILOT-001",
            "ticket_content": "The extension crashes when I open large files over 100MB. Getting error code 500 and VS Code freezes.",
            "expected_category": "bug_report"
        },
        {
            "ticket_id": "PILOT-002", 
            "ticket_content": "Would like to request a new feature for auto-completion support for custom file types. This would enhance productivity.",
            "expected_category": "feature_request"
        },
        {
            "ticket_id": "PILOT-003",
            "ticket_content": "Having trouble installing the extension. Getting permission errors during setup and configuration process.",
            "expected_category": "technical_issue"
        },
        {
            "ticket_id": "PILOT-004",
            "ticket_content": "Where can I find documentation on how to use the advanced features? Need examples and tutorials.",
            "expected_category": "documentation"
        },
        {
            "ticket_id": "PILOT-005",
            "ticket_content": "The extension is running very slow and consuming too much memory. Performance is terrible.",
            "expected_category": "performance"
        },
        {
            "ticket_id": "PILOT-006",
            "ticket_content": "Authentication failed. Can't login with my credentials. Getting access denied error repeatedly.",
            "expected_category": "authentication"
        },
        {
            "ticket_id": "PILOT-007",
            "ticket_content": "How do I integrate this extension with external APIs? Need to connect to third party services.",
            "expected_category": "integration"
        },
        {
            "ticket_id": "PILOT-008",
            "ticket_content": "The interface layout is completely broken after the last update. Buttons are not visible and UI is messy.",
            "expected_category": "ui_ux"
        },
        {
            "ticket_id": "PILOT-009",
            "ticket_content": "React extensions for smooth coding workflow. What are the best extensions for React development?",
            "expected_category": "documentation"
        },
        {
            "ticket_id": "PILOT-010",
            "ticket_content": "How many themes are available in VS Code? Want to customize the appearance and color scheme.",
            "expected_category": "documentation"
        }
    ]
    
    # Save default dataset to file
    save_pilot_dataset(default_dataset)
    return default_dataset

def save_pilot_dataset(dataset, filename="pilot_dataset_augmented.json"):
    """
    Save pilot dataset to JSON file
    
    Args:
        dataset (list): Dataset to save
        filename (str): Filename to save to
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / filename
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Saved pilot dataset with {len(dataset)} items to {filepath}")
    
    except Exception as e:
        logging.error(f"Error saving pilot dataset: {e}")

def augment_pilot_dataset(base_dataset=None):
    """
    Augment pilot dataset with additional synthetic examples
    
    Args:
        base_dataset (list): Base dataset to augment, if None creates new one
        
    Returns:
        list: Augmented dataset
    """
    if base_dataset is None:
        base_dataset = create_default_pilot_dataset()
    
    # Additional synthetic examples for better training
    augmented_examples = [
        {
            "ticket_id": "AUG-001",
            "ticket_content": "Extension won't load after VS Code update. Getting module not found errors.",
            "expected_category": "technical_issue"
        },
        {
            "ticket_id": "AUG-002",
            "ticket_content": "Please add dark mode support for the extension interface.",
            "expected_category": "feature_request"
        },
        {
            "ticket_id": "AUG-003",
            "ticket_content": "Memory leak causing VS Code to crash after using extension for extended periods.",
            "expected_category": "bug_report"
        },
        {
            "ticket_id": "AUG-004",
            "ticket_content": "OAuth token keeps expiring. Need better token refresh mechanism.",
            "expected_category": "authentication"
        },
        {
            "ticket_id": "AUG-005",
            "ticket_content": "API rate limiting issues when connecting to external services.",
            "expected_category": "integration"
        },
        {
            "ticket_id": "AUG-006",
            "ticket_content": "Toolbar buttons are misaligned and overlapping with other UI elements.",
            "expected_category": "ui_ux"
        },
        {
            "ticket_id": "AUG-007",
            "ticket_content": "Syntax highlighting not working properly. Code formatting is broken.",
            "expected_category": "bug_report"
        },
        {
            "ticket_id": "AUG-008",
            "ticket_content": "How to configure custom keybindings for the extension features?",
            "expected_category": "documentation"
        },
        {
            "ticket_id": "AUG-009",
            "ticket_content": "Extension causes high CPU usage even when idle. Performance optimization needed.",
            "expected_category": "performance"
        },
        {
            "ticket_id": "AUG-010",
            "ticket_content": "Cannot connect to company's internal API. SSL certificate issues.",
            "expected_category": "integration"
        }
    ]
    
    augmented_dataset = base_dataset + augmented_examples
    save_pilot_dataset(augmented_dataset)
    
    return augmented_dataset

def validate_dataset_format(dataset):
    """
    Validate that dataset has required fields and format
    
    Args:
        dataset (list): Dataset to validate
        
    Returns:
        bool: True if valid format
    """
    required_fields = ["ticket_id", "ticket_content", "expected_category"]
    
    if not isinstance(dataset, list):
        logging.error("Dataset must be a list")
        return False
    
    for item in dataset:
        if not isinstance(item, dict):
            logging.error(f"Dataset item must be dict: {item}")
            return False
        
        for field in required_fields:
            if field not in item:
                logging.error(f"Missing required field '{field}' in item: {item}")
                return False
            
            if not isinstance(item[field], str) or not item[field].strip():
                logging.error(f"Field '{field}' must be non-empty string in item: {item}")
                return False
    
    logging.info(f"Dataset validation passed for {len(dataset)} items")
    return True

def get_category_distribution(dataset):
    """
    Get distribution of categories in dataset
    
    Args:
        dataset (list): Dataset to analyze
        
    Returns:
        dict: Category counts
    """
    distribution = {}
    
    for item in dataset:
        category = item.get("expected_category", "unknown")
        distribution[category] = distribution.get(category, 0) + 1
    
    return distribution

def main():
    """Main function for testing and setup"""
    print("🔄 Setting up pilot dataset...")
    
    # Create or load dataset
    dataset = load_pilot_dataset()
    
    if not dataset:
        print("📝 Creating default pilot dataset...")
        dataset = create_default_pilot_dataset()
    
    # Validate format
    if validate_dataset_format(dataset):
        print("✅ Dataset format validation passed")
    else:
        print("❌ Dataset format validation failed")
        return
    
    # Show statistics
    distribution = get_category_distribution(dataset)
    print(f"\n📊 Dataset Statistics:")
    print(f"Total items: {len(dataset)}")
    print(f"Categories:")
    for category, count in sorted(distribution.items()):
        print(f"  - {category}: {count}")
    
    # Augment dataset if needed
    augment_choice = input("\n❓ Augment dataset with additional examples? (y/n): ").lower()
    if augment_choice == 'y':
        print("🔄 Augmenting dataset...")
        augmented_dataset = augment_pilot_dataset(dataset)
        print(f"✅ Augmented dataset created with {len(augmented_dataset)} items")

if __name__ == "__main__":
    main()