from abc import ABC, abstractmethod  
from dataclasses import dataclass 
 
@dataclass(frozen=True) 
class OrderPricingInput: 
    order_id: str 
    base_value_usd: float 
    weight_kg: float 
    distance_km: float 
    is_cash_on_delivery: bool 
 
# 1. Interfaz Strategy 
class ITariffCalculationStrategy(ABC): 
    @abstractmethod 
    def calculate_total_tariff(self, data: OrderPricingInput) -> float: 
        pass 
 
# 2. Estrategias Concretas 
class CrossBorderCustomsStrategy(ITariffCalculationStrategy): 
    def calculate_total_tariff(self, data: OrderPricingInput) -> float: 
        customs_duty = data.base_value_usd * 0.18 
        weight_surcharge = data.weight_kg * 4.50 
        international_freight = data.distance_km * 0.12 
        return round(customs_duty + weight_surcharge + international_freight, 2) 
 
class DomesticLastMileCODStrategy(ITariffCalculationStrategy): 
    def calculate_total_tariff(self, data: OrderPricingInput) -> float: 
        base_delivery = 3.50 + (data.distance_km * 0.25) + (data.weight_kg * 0.80) 
        cod_fee = (data.base_value_usd * 0.025) if data.is_cash_on_delivery else 0.0 
        return round(base_delivery + cod_fee, 2) 
 
class B2BContractFlatRateStrategy(ITariffCalculationStrategy): 
    def calculate_total_tariff(self, data: OrderPricingInput) -> float: 
        return round((data.weight_kg * 0.50) + (data.distance_km * 0.10), 2) 
 
# 3. Contexto de Tarificación 
class OrderPricingContext: 
    def __init__(self, strategy: ITariffCalculationStrategy) -> None: 
        self._strategy = strategy 
 
    def set_strategy(self, strategy: ITariffCalculationStrategy) -> None: 
        self._strategy = strategy 
 
    def execute_pricing(self, data: OrderPricingInput) -> float: 
        return self._strategy.calculate_total_tariff(data) 
