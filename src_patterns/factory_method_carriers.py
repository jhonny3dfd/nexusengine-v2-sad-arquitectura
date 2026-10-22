from abc import ABC, abstractmethod 
from dataclasses import dataclass 
from datetime import datetime 
from typing import Dict, Type 
 
@dataclass(frozen=True) 
class WaybillReceipt: 
    tracking_code: str 
    carrier_name: str 
    estimated_delivery: datetime 
    label_url: str 

 
# 1. Interfaz del Producto 

class IShippingCarrier(ABC): 
    @abstractmethod 
    def create_waybill(self, order_id: str, destination: str, weight_kg: float) -> WaybillReceipt: 
        pass 
 
    @abstractmethod 
    def cancel_dispatch(self, tracking_code: str) -> bool: 
        pass 
 
# 2. Productos Concretos 
class DHLInternationalCarrier(IShippingCarrier): 
    def create_waybill(self, order_id: str, destination: str, weight_kg: float) -> WaybillReceipt: 
        return WaybillReceipt( 
            tracking_code=f"DHL-INT-{order_id}", 
            carrier_name="DHL Express International", 
            estimated_delivery=datetime.now(), 
            label_url=f"https://api.dhl.com/labels/{order_id}.pdf" 
        ) 
 
    def cancel_dispatch(self, tracking_code: str) -> bool: 
        return True 
 
class OwnFleetLastMileCarrier(IShippingCarrier): 
    def create_waybill(self, order_id: str, destination: str, weight_kg: float) -> WaybillReceipt: 
        return WaybillReceipt( 
            tracking_code=f"NEXUS-LM-{order_id}", 
            carrier_name="NexusCorp Flota Propia", 
            estimated_delivery=datetime.now(), 
            label_url=f"https://internal.nexuscorp.com/qr/{order_id}.png" 
        ) 
 
    def cancel_dispatch(self, tracking_code: str) -> bool: 
        return True 
 
# 3. Clase Creadora Abstracta (Creator) 
class LogisticsCarrierCreator(ABC): 
    @abstractmethod 
    def factory_method(self) -> IShippingCarrier: 
        pass 
 
    def plan_and_dispatch(self, order_id: str, destination: str, weight_kg: float) -> WaybillReceipt: 
        carrier = self.factory_method() 
        return carrier.create_waybill(order_id, destination, weight_kg) 
 
# 4. Creadores Concretos 
class DHLCarrierCreator(LogisticsCarrierCreator): 
    def factory_method(self) -> IShippingCarrier: 
        return DHLInternationalCarrier() 
 
class OwnFleetCarrierCreator(LogisticsCarrierCreator): 
    def factory_method(self) -> IShippingCarrier: 
        return OwnFleetLastMileCarrier() 
 
# Registro de proveedores para evitar bloques if/else acoplados (ASR-03) 
CARRIER_REGISTRY: Dict[str, Type[LogisticsCarrierCreator]] = { 
    "INTERNATIONAL_DHL": DHLCarrierCreator, 
    "LOCAL_LAST_MILE": OwnFleetCarrierCreator, 
} 
