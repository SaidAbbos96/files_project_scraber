"""
Diagnostics sistemasini test qilish
"""
import asyncio
import time
from telegramuploader.utils.diagnostics import diagnostics, TelegramDiagnostics

def test_error_categorization():
    """Xato kategoriyalashni test qilish"""
    print("="*60)
    print("🧪 ERROR CATEGORIZATION TEST")
    print("="*60)
    
    test_cases = [
        ("A wait of 297 seconds is required", "rate_limit"),
        ("PEER_FLOOD: Too many requests", "flood_limit"),
        ("FILE_PARTS_INVALID: File part invalid", "file_corruption"),
        ("AUTH_KEY_INVALID: Invalid auth key", "auth_error"),
        ("CONNECTION_NOT_INITED: Not initialized", "connection_error"),
        ("Timeout error occurred", "timeout_error"),
        ("Network connection failed", "network_error"),
        ("Some unknown error", "unknown_error"),
    ]
    
    passed = 0
    failed = 0
    
    for error_msg, expected_type in test_cases:
        result_type = diagnostics.categorize_error(error_msg)
        status = "✅" if result_type == expected_type else "❌"
        
        print(f"{status} {error_msg[:40]:40} -> {result_type:20} (expected: {expected_type})")
        
        if result_type == expected_type:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Natija: {passed} ✅ / {failed} ❌")
    print("="*60 + "\n")


def test_wait_time_extraction():
    """Wait time extraction test"""
    print("="*60)
    print("🧪 WAIT TIME EXTRACTION TEST")
    print("="*60)
    
    test_cases = [
        ("A wait of 297 seconds is required", 297),
        ("A wait of 120 seconds is required", 120),
        ("Please wait of 60 seconds", 60),
        ("No wait time here", None),
    ]
    
    for error_msg, expected_time in test_cases:
        result_time = diagnostics.extract_wait_time(error_msg)
        status = "✅" if result_time == expected_time else "❌"
        
        print(f"{status} {error_msg[:40]:40} -> {result_time} (expected: {expected_time})")
    
    print("="*60 + "\n")


def test_error_logging():
    """Error logging test"""
    print("="*60)
    print("🧪 ERROR LOGGING TEST")
    print("="*60)
    
    # Test diagnostics instance
    test_diag = TelegramDiagnostics("test_diagnostics.json")
    
    # Log some test errors
    test_diag.log_error(
        filename="test_video1.mp4",
        file_size=1024*1024*100,  # 100MB
        error_msg="A wait of 300 seconds is required",
        full_traceback="Traceback...",
        duration=5.5
    )
    
    test_diag.log_error(
        filename="test_video2.mp4",
        file_size=1024*1024*200,  # 200MB
        error_msg="PEER_FLOOD: Too many requests",
        full_traceback="Traceback...",
        duration=3.2
    )
    
    test_diag.log_success("test_video3.mp4", 10.5)
    test_diag.log_success("test_video4.mp4", 15.2)
    
    print(f"✅ Logged {len(test_diag.errors)} errors")
    print(f"✅ Total attempts: {test_diag.stats.total_attempts}")
    print(f"✅ Successful: {test_diag.stats.successful_uploads}")
    print(f"✅ Failed: {test_diag.stats.failed_uploads}")
    
    # Get summary
    summary = test_diag.get_error_summary()
    print(f"\n📊 Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Get recommendations
    recommendations = test_diag.get_recommendations()
    print(f"\n💡 Recommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"   {rec}")
    
    print("="*60 + "\n")


def test_report_generation():
    """Report generation test"""
    print("="*60)
    print("🧪 REPORT GENERATION TEST")
    print("="*60)
    
    # Use the same test diagnostics
    test_diag = TelegramDiagnostics("test_diagnostics.json")
    
    # Add more test data
    for i in range(5):
        test_diag.log_error(
            filename=f"video_{i}.mp4",
            file_size=1024*1024*50,
            error_msg=f"Test error {i}",
            full_traceback="Traceback...",
            duration=2.0 + i
        )
    
    for i in range(10):
        test_diag.log_success(f"success_video_{i}.mp4", 8.0 + i)
    
    # Print report
    test_diag.print_report()
    
    print("="*60 + "\n")


async def main():
    """Run all tests"""
    print("\n🚀 DIAGNOSTICS SYSTEM TEST SUITE\n")
    
    test_error_categorization()
    await asyncio.sleep(0.5)
    
    test_wait_time_extraction()
    await asyncio.sleep(0.5)
    
    test_error_logging()
    await asyncio.sleep(0.5)
    
    test_report_generation()
    
    print("✅ All tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
