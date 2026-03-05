"""
Polymarket后台任务
每30分钟更新一次市场数据，并批量分析市场机会
"""
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.utils.logger import get_logger
from app.utils.db import get_db_connection
from app.data_sources.polymarket import PolymarketDataSource
from app.services.polymarket_batch_analyzer import PolymarketBatchAnalyzer

logger = get_logger(__name__)


class PolymarketWorker:
    """Polymarket数据更新和分析后台任务"""
    
    def __init__(self, update_interval_minutes: int = 30, analysis_cache_minutes: int = 1440):  # 24小时缓存
        """
        初始化后台任务
        
        Args:
            update_interval_minutes: 市场数据更新间隔（分钟）
            analysis_cache_minutes: AI分析结果缓存时间（分钟）
        """
        self.update_interval_minutes = update_interval_minutes
        self.analysis_cache_minutes = analysis_cache_minutes
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.polymarket_source = PolymarketDataSource()
        self.batch_analyzer = PolymarketBatchAnalyzer()
        self._last_update_ts = 0.0
        
    def start(self) -> bool:
        """启动后台任务"""
        with self._lock:
            if self._thread and self._thread.is_alive():
                return True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, name="PolymarketWorker", daemon=True)
            self._thread.start()
            logger.info(f"PolymarketWorker started (update_interval={self.update_interval_minutes}min, cache={self.analysis_cache_minutes}min)")
            return True
    
    def stop(self, timeout_sec: float = 5.0) -> None:
        """停止后台任务"""
        with self._lock:
            if not self._thread or not self._thread.is_alive():
                return
            self._stop_event.set()
            self._thread.join(timeout=timeout_sec)
            if self._thread.is_alive():
                logger.warning("PolymarketWorker thread did not stop within timeout")
            else:
                logger.info("PolymarketWorker stopped")
    
    def _run_loop(self) -> None:
        """主循环"""
        logger.info("PolymarketWorker loop started")
        
        # 启动时立即执行一次
        self._update_markets_and_analyze()
        
        while not self._stop_event.is_set():
            try:
                # 等待指定时间间隔
                wait_seconds = self.update_interval_minutes * 60
                if self._stop_event.wait(wait_seconds):
                    break  # 如果收到停止信号，退出循环
                
                # 执行更新和分析
                self._update_markets_and_analyze()
                
            except Exception as e:
                logger.error(f"PolymarketWorker loop error: {e}", exc_info=True)
                # 出错后等待1分钟再重试
                self._stop_event.wait(60)
        
        logger.info("PolymarketWorker loop stopped")
    
    def _update_markets_and_analyze(self) -> None:
        """更新市场数据并分析"""
        try:
            logger.info("Starting Polymarket data update and analysis...")
            start_time = time.time()
            
            # 1. 更新市场数据（从所有主要分类获取）
            categories = ["crypto", "politics", "economics", "sports", "tech", "finance", "geopolitics", "culture", "climate", "entertainment"]
            all_markets = []
            
            for category in categories:
                try:
                    markets = self.polymarket_source.get_trending_markets(category, limit=50)
                    all_markets.extend(markets)
                    logger.info(f"Fetched {len(markets)} markets from category: {category}")
                except Exception as e:
                    logger.warning(f"Failed to fetch markets for category {category}: {e}")
            
            # 去重（按market_id）
            unique_markets = {}
            for market in all_markets:
                market_id = market.get('market_id')
                if market_id:
                    unique_markets[market_id] = market
            
            logger.info(f"Total unique markets: {len(unique_markets)}")
            
            # 2. 批量分析市场（一次性分析所有市场，由AI筛选机会）
            markets_list = list(unique_markets.values())
            logger.info(f"Starting batch analysis for {len(markets_list)} markets...")
            
            # 优化策略：先用规则筛选，只对高价值机会调用LLM
            # 这样可以大幅减少LLM调用次数，节省token
            
            # 1. 先用规则筛选出最有价值的机会（不调用LLM）
            rule_based_opportunities = []
            for market in markets_list:
                prob = market.get('current_probability', 50.0)
                volume = market.get('volume_24h', 0)
                divergence = abs(prob - 50.0)
                
                # 规则筛选：高交易量 + 明显概率偏差
                if volume > 5000 and divergence > 8:
                    rule_based_opportunities.append(market)
            
            # 2. 只对规则筛选出的机会调用LLM（最多30个，节省token）
            if rule_based_opportunities:
                logger.info(f"Rule-based filtering: {len(rule_based_opportunities)} opportunities, analyzing top 30 with LLM")
                # 按交易量和概率偏差排序，取前30个
                rule_based_opportunities.sort(
                    key=lambda x: (x.get('volume_24h', 0) * abs(x.get('current_probability', 50) - 50)),
                    reverse=True
                )
                top_opportunities = rule_based_opportunities[:30]
                
                analyzed_markets = self.batch_analyzer.batch_analyze_markets(
                    top_opportunities,
                    max_opportunities=30  # 只分析30个最有价值的机会
                )
            else:
                logger.info("No rule-based opportunities found, skipping LLM analysis")
                analyzed_markets = []
            
            # 3. 保存分析结果到数据库
            if analyzed_markets:
                self.batch_analyzer.save_batch_analysis(analyzed_markets)
                analyzed_count = len(analyzed_markets)
            else:
                analyzed_count = 0
            
            elapsed = time.time() - start_time
            logger.info(f"Polymarket update completed: {len(unique_markets)} markets updated, {analyzed_count} opportunities identified in {elapsed:.1f}s")
            self._last_update_ts = time.time()
            
        except Exception as e:
            logger.error(f"Failed to update markets and analyze: {e}", exc_info=True)
    
    
    def force_update(self) -> None:
        """强制立即更新（用于手动触发）"""
        logger.info("Force update triggered")
        self._update_markets_and_analyze()


# 全局单例
_polymarket_worker: Optional[PolymarketWorker] = None
_worker_lock = threading.Lock()


def get_polymarket_worker() -> PolymarketWorker:
    """获取PolymarketWorker单例"""
    global _polymarket_worker
    with _worker_lock:
        if _polymarket_worker is None:
            update_interval = int(os.getenv("POLYMARKET_UPDATE_INTERVAL_MIN", "30"))
            cache_minutes = int(os.getenv("POLYMARKET_ANALYSIS_CACHE_MIN", "30"))
            _polymarket_worker = PolymarketWorker(
                update_interval_minutes=update_interval,
                analysis_cache_minutes=cache_minutes
            )
        return _polymarket_worker


# 需要导入os
import os
