"""
Legacy Adapter - Backward compatibility with old downloader.runner
"""
import asyncio
from typing import Dict, Any

from utils.logger_core import logger
from .orchestrator import FileDownloaderOrchestrator


async def download(config: Dict[str, Any]) -> None:
    """
    Legacy download function - backward compatibility
    
    Bu funksiya eski downloader.runner.download() funksiyasi bilan
    bir xil interface ni ta'minlaydi, lekin ichida yangi professional
    FileDownloaderOrchestrator sistemasini ishlatadi.
    
    Args:
        config: Configuration dictionary (APP_CONFIG + SITE_CONFIG)
    """
    site_name = config.get("name", "unknown")
    debug_mode = config.get("debug", False)
    mode = config.get("mode", "parallel")
    
    logger.info(f"🚀 Starting download with new FileDownloader system")
    logger.info(f"📂 Site: {site_name}")
    logger.info(f"🔧 Mode: {mode}")
    logger.info(f"🐛 Debug: {debug_mode}")
    
    try:
        # Yangi orchestrator yaratish
        orchestrator = FileDownloaderOrchestrator(config)
        
        # Download statistikalarini ko'rsatish
        orchestrator.log_download_statistics(site_name)
        
        # Download mode bo'yicha ishga tushirish
        if mode == "sequential":
            result = await orchestrator.sequential_download(site_name)
        else:
            result = await orchestrator.parallel_download(site_name)
        
        # Natijalarni log qilish
        if result["status"] == "completed":
            stats = result.get("statistics", {})
            logger.info(f"✅ Download completed!")
            logger.info(f"   📊 Total: {stats.get('total', 0)}")
            logger.info(f"   ✅ Success: {stats.get('success', 0)}")
            logger.info(f"   ♻️ Existed: {stats.get('exists', 0)}")
            logger.info(f"   ❌ Failed: {stats.get('failed', 0)}")
            logger.info(f"   ⏭️ Skipped: {stats.get('skipped', 0)}")
            logger.info(f"   💾 Size: {stats.get('total_size_gb', 0):.2f} GB")
            logger.info(f"   📈 Success rate: {stats.get('success_rate', 0):.1f}%")
        
        elif result["status"] == "no_files":
            logger.warning("⚠️ No files found for download")
        
        elif result["status"] == "cancelled":
            logger.info("🚫 Download cancelled by user")
        
        else:
            logger.error(f"❌ Download failed: {result.get('status')}")
            
    except Exception as e:
        logger.error(f"❌ Download error: {e}")
        raise


# Qo'shimcha legacy functions (agar kerak bo'lsa)

async def download_with_stats(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Download with statistics return - extended legacy function
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Download results and statistics
    """
    site_name = config.get("name", "unknown")
    orchestrator = FileDownloaderOrchestrator(config)
    
    # Statistics olish
    initial_stats = orchestrator.get_download_statistics(site_name)
    
    # Download qilish
    result = await orchestrator.download_files(site_name, debug_mode=config.get("debug", False))
    
    # Final statistics
    final_stats = orchestrator.get_download_statistics(site_name)
    
    return {
        "download_result": result,
        "initial_stats": initial_stats,
        "final_stats": final_stats,
        "site_name": site_name
    }


async def sequential_mode(config: Dict[str, Any]) -> None:
    """Legacy sequential mode function"""
    config_copy = config.copy()
    config_copy["mode"] = "sequential"
    await download(config_copy)


async def parallel_mode(config: Dict[str, Any]) -> None:
    """Legacy parallel mode function"""  
    config_copy = config.copy()
    config_copy["mode"] = "parallel"
    await download(config_copy)


# Debug/Test functions

async def debug_download_single_file(config: Dict[str, Any]) -> None:
    """Debug mode - single file download"""
    config_copy = config.copy()
    config_copy["debug"] = True
    await download(config_copy)


def get_download_status(site_name: str) -> Dict[str, Any]:
    """Get current download status for a site"""
    # Temporary config for database access
    temp_config = {"download_dir": "../downloads", "download_concurrency": 1}
    orchestrator = FileDownloaderOrchestrator(temp_config)
    return orchestrator.get_download_statistics(site_name)