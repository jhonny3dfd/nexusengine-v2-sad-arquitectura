from abc import ABC, abstractmethod 
from dataclasses import dataclass 
import hashlib 
 
@dataclass(frozen=True) 
class PaymentResult: 
    is_authorized: bool 
    transaction_id: str 
    audit_signature_sha256: str 
 
# 1. Interfaz Target (Estándar interno de NexusCorp bajo PCI-DSS) 
class IPaymentGatewayPort(ABC): 
    @abstractmethod 
    def authorize_payment( 
        self, order_id: str, pci_token: str, amount_cents: int, currency: str 
    ) -> PaymentResult: 
        pass 
 
    @abstractmethod 
    def capture_funds(self, transaction_id: str) -> bool: 
        pass 
 
# 2. Adaptee (SDK externo incompatible de billetera digital) 
class LatamDigitalWalletSDK: 
    def execute_xml_charge(self, wallet_hash: str, decimal_value: float, iso_curr: str) -> dict: 
        return {"status_code": 200, "ext_tx_ref": "WALLET-TX-998877"} 
 
    def commit_tx(self, external_ref: str) -> int: 
        return 1 
 
# 3. Adapter (Traduce llamadas del dominio al SDK externo) 
class LatamWalletPaymentAdapter(IPaymentGatewayPort): 
    def __init__(self, sdk: LatamDigitalWalletSDK) -> None: 
        self._sdk = sdk 
 
    def authorize_payment( 
        self, order_id: str, pci_token: str, amount_cents: int, currency: str 
    ) -> PaymentResult: 
        decimal_amount = round(amount_cents / 100.0, 2) 
        raw_response = self._sdk.execute_xml_charge( 
            wallet_hash=pci_token, 
            decimal_value=decimal_amount, 
            iso_curr=currency 
        ) 
        authorized = raw_response.get("status_code") == 200 
        tx_id = raw_response.get("ext_tx_ref", "FAILED") 
 
        # Firma SHA-256 para el registro inmutable de auditoría (ASR-04) 
        payload = f"{order_id}:{tx_id}:{amount_cents}:{currency}" 
        signature = hashlib.sha256(payload.encode("utf-8")).hexdigest() 
 
        return PaymentResult( 
            is_authorized=authorized, 
            transaction_id=tx_id, 
            audit_signature_sha256=signature 
        ) 
 
    def capture_funds(self, transaction_id: str) -> bool: 
        return self._sdk.commit_tx(transaction_id) == 1 
