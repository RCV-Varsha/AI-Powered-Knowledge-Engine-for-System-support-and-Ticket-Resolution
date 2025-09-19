import os
import sys
import json
from pathlib import Path
import logging

# Add src directory to path for imports
sys.path.append('src')

from resolver import MultiModelResolver
from augment_dataset import load_pilot_dataset, save_pilot_dataset, create_default_pilot_dataset

def setup_validation_environment():
    """Setup environment for validation"""
    print("🔧 Setting up validation environment...")
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Check if pilot dataset exists, create if not
    dataset_path = data_dir / "pilot_dataset_augmented.json"
    if not dataset_path.exists():
        print("📝 Creating pilot dataset...")
        dataset = create_default_pilot_dataset()
        save_pilot_dataset(dataset)
    else:
        print("✅ Pilot dataset found")
    
    return True

def validate_with_pilot_dataset(llm_provider="gemini"):
    """
    Validate categorization accuracy using pilot dataset
    
    Args:
        llm_provider (str): LLM provider to use ("gemini" or "openai")
    
    Returns:
        dict: Validation results
    """
    print(f"\n🎯 VALIDATING CATEGORIZATION WITH {llm_provider.upper()}")
    print("=" * 60)
    
    try:
        # Initialize resolver
        resolver = MultiModelResolver(llm_provider=llm_provider)
        
        # Load pilot dataset
        pilot_dataset = load_pilot_dataset()
        if not pilot_dataset:
            print("⚠️ No pilot dataset loaded.")
            return None
        
        print(f"📊 Testing {len(pilot_dataset)} tickets...")
        
        correct = 0
        total = len(pilot_dataset)
        detailed_results = []
        
        for i, t in enumerate(pilot_dataset, 1):
            ticket_id = t.get("ticket_id", f"UNKNOWN-{i}")
            ticket_content = t.get("ticket_content", "")
            expected_category = t.get("expected_category", "unknown")
            
            print(f"\n🎫 Testing {i}/{total}: {ticket_id}")
            print(f"📝 Content: {ticket_content[:60]}...")
            
            # Get prediction
            predicted, source = resolver.safe_categorize_ticket(ticket_content)
            
            # Normalize for comparison (case/underscores)
            expected_norm = expected_category.strip().lower().replace(" ", "_")
            predicted_norm = predicted.strip().lower().replace(" ", "_")
            
            is_correct = predicted_norm == expected_norm
            if is_correct:
                correct += 1
            
            detailed_results.append({
                "ticket_id": ticket_id,
                "ticket_content": ticket_content,
                "expected": expected_norm,
                "predicted": predicted_norm,
                "is_correct": is_correct,
                "source": source
            })
            
            status = "✅" if is_correct else "❌"
            print(f"🎯 Expected: {expected_norm}")
            print(f"🔮 Predicted: {predicted_norm}")
            print(f"📍 Source: {source}")
            print(f"🏆 Result: {status}")
        
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"🎉 VALIDATION RESULTS ({llm_provider.upper()})")
        print(f"{'='*60}")
        print(f"✅ Correct: {correct}/{total}")
        print(f"📊 Accuracy: {accuracy:.2f}%")
        print(f"🔧 Provider: {llm_provider}")
        
        # Source breakdown
        source_counts = {}
        for result in detailed_results:
            source = result["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print(f"\n📈 Source Breakdown:")
        for source, count in source_counts.items():
            print(f"   • {source}: {count} predictions")
        
        # Save results
        results_file = f"validation_results_{llm_provider}.json"
        try:
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump({
                    "provider": llm_provider,
                    "accuracy": accuracy,
                    "correct": correct,
                    "total": total,
                    "source_breakdown": source_counts,
                    "detailed_results": detailed_results
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to {results_file}")
        except Exception as e:
            print(f"⚠️ Could not save results: {e}")
        
        return {
            "provider": llm_provider,
            "accuracy": accuracy,
            "correct": correct,
            "total": total,
            "detailed_results": detailed_results
        }
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        logging.error(f"Validation error: {e}", exc_info=True)
        return None

def validate_solution_generation(llm_provider="gemini", num_samples=3):
    """
    Test solution generation quality
    
    Args:
        llm_provider (str): LLM provider to use
        num_samples (int): Number of samples to test
    """
    print(f"\n🧪 TESTING SOLUTION GENERATION WITH {llm_provider.upper()}")
    print("=" * 60)
    
    try:
        resolver = MultiModelResolver(llm_provider=llm_provider)
        pilot_dataset = load_pilot_dataset()
        
        if not pilot_dataset:
            print("⚠️ No pilot dataset for solution testing")
            return
        
        # Test first few samples
        samples = pilot_dataset[:num_samples]
        
        for i, sample in enumerate(samples, 1):
            ticket_id = sample.get("ticket_id", f"TEST-{i}")
            content = sample.get("ticket_content", "")
            category = sample.get("expected_category", "uncategorized")
            
            print(f"\n🎫 Solution Test {i}/{len(samples)}: {ticket_id}")
            print(f"📂 Category: {category}")
            print(f"📝 Content: {content[:80]}...")
            
            # Generate solution
            solution, source = resolver.safe_generate_solution(content, category, "")
            
            print(f"🤖 Solution Source: {source}")
            print(f"💡 Generated Solution:")
            print("-" * 40)
            print(solution[:300] + ("..." if len(solution) > 300 else ""))
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Solution generation test failed: {e}")

def test_system_components():
    """Test individual system components"""
    print("\n🔍 TESTING SYSTEM COMPONENTS")
    print("=" * 60)
    
    components_status = {}
    
    # Test 1: Environment variables
    print("\n1. 🔑 Environment Variables:")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    components_status["google_api_key"] = bool(google_api_key)
    components_status["openai_api_key"] = bool(openai_api_key)
    
    print(f"   Google API Key: {'✅' if google_api_key else '❌'}")
    print(f"   OpenAI API Key: {'✅' if openai_api_key else '❌'}")
    
    # Test 2: Data files
    print("\n2. 📁 Data Files:")
    dataset_path = Path("data/pilot_dataset_augmented.json")
    vectorstore_path = Path("vectorstore/db_faiss")
    
    components_status["pilot_dataset"] = dataset_path.exists()
    components_status["vectorstore"] = vectorstore_path.exists()
    
    print(f"   Pilot Dataset: {'✅' if dataset_path.exists() else '❌'}")
    print(f"   Vector Store: {'✅' if vectorstore_path.exists() else '❌'}")
    
    # Test 3: Dependencies
    print("\n3. 📦 Dependencies:")
    try:
        import langchain_community
        components_status["langchain_community"] = True
        print("   LangChain Community: ✅")
    except ImportError:
        components_status["langchain_community"] = False
        print("   LangChain Community: ❌")
    
    try:
        import langchain_google_genai
        components_status["langchain_google_genai"] = True
        print("   LangChain Google GenAI: ✅")
    except ImportError:
        components_status["langchain_google_genai"] = False
        print("   LangChain Google GenAI: ❌")
    
    try:
        import faiss
        components_status["faiss"] = True
        print("   FAISS: ✅")
    except ImportError:
        components_status["faiss"] = False
        print("   FAISS: ❌")
    
    # Test 4: Resolver initialization
    print("\n4. 🧠 Resolver Initialization:")
    try:
        resolver = MultiModelResolver(llm_provider="gemini")
        components_status["resolver_init"] = True
        print("   MultiModelResolver: ✅")
        
        # Test basic functionality
        test_content = "This is a test ticket about a bug in the extension"
        category, source = resolver.safe_categorize_ticket(test_content)
        components_status["categorization"] = True
        print(f"   Categorization Test: ✅ ({category}, {source})")
        
    except Exception as e:
        components_status["resolver_init"] = False
        components_status["categorization"] = False
        print(f"   MultiModelResolver: ❌ ({e})")
    
    return components_status

def main():
    """Main validation function"""
    print("🚀 AI-POWERED SUPPORT SYSTEM VALIDATION")
    print("=" * 60)
    
    # Setup environment
    setup_validation_environment()
    
    # Test system components
    component_results = test_system_components()
    
    # Run validation tests
    print("\n" + "=" * 60)
    print("🎯 RUNNING VALIDATION TESTS")
    print("=" * 60)
    
    providers_to_test = []
    if component_results.get("google_api_key"):
        providers_to_test.append("gemini")
    if component_results.get("openai_api_key"):
        providers_to_test.append("openai")
    
    if not providers_to_test:
        print("⚠️ No API keys found. Testing with template fallbacks only...")
        providers_to_test = ["gemini"]  # Test fallback behavior
    
    validation_results = {}
    
    for provider in providers_to_test:
        print(f"\n🔄 Testing with {provider.upper()}...")
        
        # Categorization validation
        results = validate_with_pilot_dataset(provider)
        if results:
            validation_results[provider] = results
        
        # Solution generation testing
        validate_solution_generation(provider, num_samples=3)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    
    if validation_results:
        for provider, results in validation_results.items():
            print(f"{provider.upper()}: {results['accuracy']:.2f}% accuracy ({results['correct']}/{results['total']})")
    
    # Component health check
    print(f"\n🏥 System Health:")
    health_score = sum(1 for v in component_results.values() if v) / len(component_results) * 100
    print(f"Overall Health: {health_score:.1f}%")
    
    critical_components = ["resolver_init", "categorization"]
    critical_health = all(component_results.get(comp, False) for comp in critical_components)
    
    if critical_health:
        print("✅ System is operational")
    else:
        print("⚠️ System has critical issues")
        print("Missing critical components:")
        for comp in critical_components:
            if not component_results.get(comp, False):
                print(f"  - {comp}")
    
    return validation_results

if __name__ == "__main__":
    main()