#!/usr/bin/env python3
"""
ReggieStarr GUI - Full Tkinter Interface for TEC MA-79 Digital Cash Register
Complete Point-of-Sale System with Touchscreen Interface

Author: Performance Supply Depot LLC
Version: 4.1.0
Date: February 18, 2026
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import json
import sqlite3
import urllib.request
import urllib.error
import sys
import time
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# Optional imports for advanced features
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# Optional sound for bell/alert
try:
    import winsound  # Windows
    SOUND_AVAILABLE = True
except ImportError:
    try:
        import subprocess  # Linux/macOS
        SOUND_AVAILABLE = True
    except ImportError:
        SOUND_AVAILABLE = False

# ==================== CONFIGURATION ====================

class Config:
    STORE_NAME = "Performance Supply Depot"
    STORE_ADDRESS = "123 Main Street, Berkeley, CA 94702"
    STORE_PHONE = "(510) 555-0123"
    
    CURRENCY_SYMBOL = "$"
    
    # TEC MA-79 Style Tax Rates
    TAX_RATES = {
        'Berkeley': 0.1025,
        'VapeTax': 0.125,
        'State': 0.0725,
        'Local': 0.01,
    }
    
    # CRV (California Redemption Value) Rates
    CRV_RATES = {
        0.05: "Small Bottle (≤24oz)",
        0.10: "Large Bottle (>24oz)",
    }
    
    PAYMENT_METHODS = [
        'Cash', 'Credit Card', 'Debit Card', 'Bitcoin (BTC)',
        'EBT', 'WIC', 'Check', 'Store Credit', 'Gift Card'
    ]
    
    # TEC MA-79 Modes
    MODES = {
        'Register': 'Normal sales transactions',
        'Void': 'Cancel previous transactions',
        'X': 'Read reports without reset',
        'Z': 'Read and reset reports',
        'Program': 'Configure settings',
        'Service': 'Maintenance mode',
        'Negative': 'Returns and refunds'
    }
    
    # Multilingual Support (11 languages from v1.0.1.6)
    LANGUAGES = {
        'English': {
            'product_code': 'Product Code', 'quantity': 'Quantity', 'price': 'Price',
            'add_product': 'Add Product', 'discount': 'Discount (%)', 'surcharge': 'Surcharge ($)',
            'payment_method': 'Payment Method', 'refund': 'Refund', 'void': 'Void',
            'exchange': 'Exchange', 'cancel': 'Cancel Transaction', 'generate_report': 'Generate Report',
            'login': 'Login', 'logout': 'Logout', 'hold': 'Hold', 'recall': 'Recall',
            'split_check': 'Split Check', 'split_tender': 'Split Tender', 'convert': 'Convert Currency',
            'qr_code': 'QR Code', 'crypto_tax': 'Crypto Tax Report', 'reward_customer': 'Reward Customer',
            'ai_pricing': 'AI Price Suggestions', 'multi_store': 'Multi-Store Analytics',
            'hand_mode': 'Hand Mode', 'palette': 'Palette', 'reprint_receipt': 'Reprint Receipt',
            'card_payment': 'Card Payment', 'update_config': 'Update Config', 'redeem_points': 'Redeem Points',
            'print_label': 'Print Label', 'track_pour': 'Track Pour', 'move_crypto': 'Move Crypto',
            'fetch_orders': 'Fetch Online Orders', 'pay': 'Pay', 'subtotal': 'Subtotal', 'tax': 'Tax',
            'total': 'TOTAL', 'change': 'Change', 'welcome': 'Welcome', 'thank_you': 'Thank you for shopping with us!',
            'item_correct': 'Item Correction', 'return_merchandise': 'Return Merchandise', 'multiplier': 'Multiplier',
            'bag_fee': 'Bag Fee', 'atm_fee': 'ATM Fee', 'scale': 'Scale', 'tare': 'Tare', 'apply_tare': 'Apply Tare'
        },
        'Spanish': {
            'product_code': 'Código de Producto', 'quantity': 'Cantidad', 'price': 'Precio',
            'add_product': 'Agregar Producto', 'discount': 'Descuento (%)', 'surcharge': 'Recargo ($)',
            'payment_method': 'Método de Pago', 'refund': 'Reembolso', 'void': 'Anular',
            'exchange': 'Intercambiar', 'cancel': 'Cancelar Transacción', 'generate_report': 'Generar Informe',
            'login': 'Iniciar sesión', 'logout': 'Cerrar sesión', 'hold': 'Espera', 'recall': 'Recordar',
            'split_check': 'Dividir Cheque', 'split_tender': 'Dividir Pago', 'convert': 'Convertir Moneda',
            'qr_code': 'Código QR', 'crypto_tax': 'Informe de Impuestos Cripto', 'reward_customer': 'Recompensar Cliente',
            'ai_pricing': 'Sugerencias de Precios AI', 'multi_store': 'Análisis Multi-Tienda',
            'hand_mode': 'Modo de Mano', 'palette': 'Paleta', 'reprint_receipt': 'Reimprimir Recibo',
            'card_payment': 'Pago con Tarjeta', 'update_config': 'Actualizar Configuración', 'redeem_points': 'Canjear Puntos',
            'print_label': 'Imprimir Etiqueta', 'track_pour': 'Rastrear Vertido', 'move_crypto': 'Mover Cripto',
            'fetch_orders': 'Obtener Pedidos en Línea', 'pay': 'Pagar', 'subtotal': 'Subtotal', 'tax': 'Impuesto',
            'total': 'TOTAL', 'change': 'Cambio', 'welcome': 'Bienvenido', 'thank_you': '¡Gracias por comprar con nosotros!',
            'item_correct': 'Corrección de Artículo', 'return_merchandise': 'Devolución de Mercancía', 'multiplier': 'Multiplicador',
            'bag_fee': 'Tarifa de Bolsa', 'atm_fee': 'Tarifa ATM', 'scale': 'Escala', 'tare': 'Tara', 'apply_tare': 'Aplicar Tara'
        },
        'Turkish': {
            'product_code': 'Ürün Kodu', 'quantity': 'Miktar', 'price': 'Fiyat',
            'add_product': 'Ürün Ekle', 'discount': 'İndirim (%)', 'surcharge': 'Ek Ücret ($)',
            'payment_method': 'Ödeme Yöntemi', 'refund': 'İade', 'void': 'İptal',
            'exchange': 'Değişim', 'cancel': 'İşlemi İptal Et', 'generate_report': 'Rapor Oluştur',
            'login': 'Giriş', 'logout': 'Çıkış', 'hold': 'Beklet', 'recall': 'Geri Çağır',
            'split_check': 'Hesabı Böl', 'split_tender': 'Ödemeyi Böl', 'convert': 'Para Birimi Dönüştür',
            'qr_code': 'QR Kodu', 'crypto_tax': 'Kripto Vergi Raporu', 'reward_customer': 'Müşteriyi Ödüllendir',
            'ai_pricing': 'AI Fiyat Önerileri', 'multi_store': 'Çoklu Mağaza Analizi',
            'hand_mode': 'El Modu', 'palette': 'Palet', 'reprint_receipt': 'Makbuzu Yeniden Yazdır',
            'card_payment': 'Kart Ödemesi', 'update_config': 'Yapılandırmayı Güncelle', 'redeem_points': 'Puanları Kullan',
            'print_label': 'Etiket Yazdır', 'track_pour': 'Dökümü Takip Et', 'move_crypto': 'Kripto Taşı',
            'fetch_orders': 'Çevrimiçi Siparişleri Al', 'pay': 'Ödeme', 'subtotal': 'Ara Toplam', 'tax': 'Vergi',
            'total': 'TOPLAM', 'change': 'Para Üstü', 'welcome': 'Hoş Geldiniz', 'thank_you': 'Teşekkürler!',
            'item_correct': 'Ürün Düzeltme', 'return_merchandise': 'Malları İade', 'multiplier': 'Çarpan',
            'bag_fee': 'Torba Ücreti', 'atm_fee': 'ATM Ücreti', 'scale': 'Terazi', 'tare': 'Dara', 'apply_tare': 'Dara Uygula'
        },
        'German': {
            'product_code': 'Produktcode', 'quantity': 'Menge', 'price': 'Preis',
            'add_product': 'Produkt Hinzufügen', 'discount': 'Rabatt (%)', 'surcharge': 'Aufschlag ($)',
            'payment_method': 'Zahlungsmethode', 'refund': 'Rückerstattung', 'void': 'Stornieren',
            'exchange': 'Umtausch', 'cancel': 'Transaktion Abbrechen', 'generate_report': 'Bericht Erstellen',
            'login': 'Anmelden', 'logout': 'Abmelden', 'hold': 'Halten', 'recall': 'Abrufen',
            'split_check': 'Rechnung Teilen', 'split_tender': 'Zahlung Teilen', 'convert': 'Währung Umrechnen',
            'qr_code': 'QR-Code', 'crypto_tax': 'Krypto-Steuerbericht', 'reward_customer': 'Kunde Belohnen',
            'ai_pricing': 'KI-Preise', 'multi_store': 'Multi-Store Analyse', 'hand_mode': 'Handmodus',
            'palette': 'Palette', 'reprint_receipt': 'Beleg Nachdrucken', 'card_payment': 'Kartenzahlung',
            'update_config': 'Konfiguration Aktualisieren', 'redeem_points': 'Punkte Einlösen', 'print_label': 'Etikett Drucken',
            'track_pour': 'Ausguss Verfolgen', 'move_crypto': 'Krypto Verschieben', 'fetch_orders': 'Online-Bestellungen Abrufen',
            'pay': 'Bezahlen', 'subtotal': 'Zwischensumme', 'tax': 'Steuer', 'total': 'GESAMT',
            'change': 'Wechselgeld', 'welcome': 'Willkommen', 'thank_you': 'Vielen Dank!',
            'item_correct': 'Artikelkorrektur', 'return_merchandise': 'Ware Zurückgeben', 'multiplier': 'Multiplikator',
            'bag_fee': 'Tütengebühr', 'atm_fee': 'ATM-Gebühr', 'scale': 'Waage', 'tare': 'Taragewicht', 'apply_tare': 'Tare Anwenden'
        },
        'Portuguese': {
            'product_code': 'Código do Produto', 'quantity': 'Quantidade', 'price': 'Preço',
            'add_product': 'Adicionar Produto', 'discount': 'Desconto (%)', 'surcharge': 'Taxa Adicional ($)',
            'payment_method': 'Método de Pagamento', 'refund': 'Reembolso', 'void': 'Anular',
            'exchange': 'Trocar', 'cancel': 'Cancelar Transação', 'generate_report': 'Gerar Relatório',
            'login': 'Entrar', 'logout': 'Sair', 'hold': 'Segurar', 'recall': 'Lembrar',
            'split_check': 'Dividir Conta', 'split_tender': 'Dividir Pagamento', 'convert': 'Converter Moeda',
            'qr_code': 'Código QR', 'crypto_tax': 'Relatório de Impostos Crypto', 'reward_customer': 'Recompensar Cliente',
            'ai_pricing': 'Sugestões de Preço IA', 'multi_store': 'Análise Multi-Loja', 'hand_mode': 'Modo Manual',
            'palette': 'Paleta', 'reprint_receipt': 'Reimprimir Recibo', 'card_payment': 'Pagamento com Cartão',
            'update_config': 'Atualizar Configuração', 'redeem_points': 'Resgatar Pontos', 'print_label': 'Imprimir Etiqueta',
            'track_pour': 'Rastrear Dose', 'move_crypto': 'Mover Cripto', 'fetch_orders': 'Buscar Pedidos Online',
            'pay': 'Pagar', 'subtotal': 'Subtotal', 'tax': 'Imposto', 'total': 'TOTAL',
            'change': 'Troco', 'welcome': 'Bem-vindo', 'thank_you': 'Obrigado!',
            'item_correct': 'Correção de Item', 'return_merchandise': 'Devolução de Mercadoria', 'multiplier': 'Multiplicador',
            'bag_fee': 'Taxa de Saco', 'atm_fee': 'Taxa ATM', 'scale': 'Balança', 'tare': 'Tara', 'apply_tare': 'Aplicar Tara'
        },
        'Italian': {
            'product_code': 'Codice Prodotto', 'quantity': 'Quantità', 'price': 'Prezzo',
            'add_product': 'Aggiungi Prodotto', 'discount': 'Sconto (%)', 'surcharge': 'Supplemento ($)',
            'payment_method': 'Metodo di Pagamento', 'refund': 'Rimborso', 'void': 'Annulla',
            'exchange': 'Scambia', 'cancel': 'Annulla Transazione', 'generate_report': 'Genera Rapporto',
            'login': 'Accedi', 'logout': 'Esci', 'hold': 'Tieni', 'recall': 'Richiama',
            'split_check': 'Dividi Conto', 'split_tender': 'Dividi Pagamento', 'convert': 'Converti Valuta',
            'qr_code': 'Codice QR', 'crypto_tax': 'Report Fiscale Crypto', 'reward_customer': 'Ricompensa Cliente',
            'ai_pricing': 'Suggerimenti Prezzo AI', 'multi_store': 'Analisi Multi-Negozio', 'hand_mode': 'Modalità Manuale',
            'palette': 'Paletta', 'reprint_receipt': 'Ristampa Scontrino', 'card_payment': 'Pagamento Carta',
            'update_config': 'Aggiorna Configurazione', 'redeem_points': 'Riscuoti Punti', 'print_label': 'Stampa Etichetta',
            'track_pour': 'Traccia Versamento', 'move_crypto': 'Sposta Cripto', 'fetch_orders': 'Carica Ordini Online',
            'pay': 'Paga', 'subtotal': 'Subtotale', 'tax': 'Imposta', 'total': 'TOTALE',
            'change': 'Resto', 'welcome': 'Benvenuto', 'thank_you': 'Grazie!',
            'item_correct': 'Correzione Articolo', 'return_merchandise': 'Restituzione Merce', 'multiplier': 'Moltiplicatore',
            'bag_fee': 'Costo Sacchetto', 'atm_fee': 'Costo ATM', 'scale': 'Bilancia', 'tare': 'Tara', 'apply_tare': 'Applica Tara'
        },
        'Chinese': {
            'product_code': '产品代码', 'quantity': '数量', 'price': '价格',
            'add_product': '添加产品', 'discount': '折扣 (%)', 'surcharge': '附加费 ($)',
            'payment_method': '付款方式', 'refund': '退款', 'void': '作废',
            'exchange': '兑换', 'cancel': '取消交易', 'generate_report': '生成报告',
            'login': '登录', 'logout': '登出', 'hold': '挂单', 'recall': '召回',
            'split_check': '分单', 'split_tender': '分拆付款', 'convert': '货币转换',
            'qr_code': '二维码', 'crypto_tax': '加密税务报告', 'reward_customer': '奖励客户',
            'ai_pricing': 'AI价格建议', 'multi_store': '多店铺分析', 'hand_mode': '手动模式',
            'palette': '调色板', 'reprint_receipt': '重印收据', 'card_payment': '卡片支付',
            'update_config': '更新配置', 'redeem_points': '兑换积分', 'print_label': '打印标签',
            'track_pour': '追踪倒酒', 'move_crypto': '转移加密货币', 'fetch_orders': '获取在线订单',
            'pay': '支付', 'subtotal': '小计', 'tax': '税', 'total': '总计',
            'change': '找零', 'welcome': '欢迎', 'thank_you': '谢谢！',
            'item_correct': '商品纠错', 'return_merchandise': '商品退货', 'multiplier': '乘数',
            'bag_fee': '袋子费', 'atm_fee': 'ATM费', 'scale': '秤', 'tare': '皮重', 'apply_tare': '应用皮重'
        },
        'Japanese': {
            'product_code': '商品コード', 'quantity': '数量', 'price': '価格',
            'add_product': '商品追加', 'discount': '割引 (%)', 'surcharge': '追加料金 ($)',
            'payment_method': '支払方法', 'refund': '返金', 'void': '取消',
            'exchange': '交換', 'cancel': '取引取消', 'generate_report': 'レポート作成',
            'login': 'ログイン', 'logout': 'ログアウト', 'hold': '保持', 'recall': '召喚',
            'split_check': '分割請求', 'split_tender': '分割支払', 'convert': '通貨換算',
            'qr_code': 'QRコード', 'crypto_tax': 'سسة報告', 'reward_customer': '顧客奖励',
            'ai_pricing': 'AI価格提案', 'multi_store': 'マルチストア分析', 'hand_mode': '.handモード',
            'palette': 'パレット', 'reprint_receipt': 'レシート再印刷', 'card_payment': 'カード決済',
            'update_config': '設定更新', 'redeem_points': 'ポイント換金', 'print_label': 'ラベル印刷',
            'track_pour': '注ぐを追跡', 'move_crypto': '.moveする', 'fetch_orders': 'オンライン注文を取得',
            'pay': '支払う', 'subtotal': '小計', 'tax': '税', 'total': '合計',
            'change': 'お釣り', 'welcome': 'ようこそ', 'thank_you': 'ありがとう！',
            'item_correct': 'アイテム修正', 'return_merchandise': ' 商品退货', 'multiplier': '乗数',
            'bag_fee': '袋料金', 'atm_fee': 'ATM料金', 'scale': 'スケール', 'tare': '風袋', 'apply_tare': '風袋適応'
        },
        'Korean': {
            'product_code': '제품 코드', 'quantity': '수량', 'price': '가격',
            'add_product': '제품 추가', 'discount': '할인 (%)', 'surcharge': '추가 요금 ($)',
            'payment_method': '결제 방법', 'refund': '환불', 'void': '취소',
            'exchange': '환전', 'cancel': '거래 취소', 'generate_report': '보고서 생성',
            'login': '로그인', 'logout': '로그아웃', 'hold': '보류', 'recall': '호출',
            'split_check': '청구서 분할', 'split_tender': '결제 분할', 'convert': '환율 변환',
            'qr_code': 'QR 코드', 'crypto_tax': '크립토세 보고서', 'reward_customer': '고객 보상',
            'ai_pricing': 'AI 가격 제안', 'multi_store': '멀티 스토어 분석', 'hand_mode': '핸드 모드',
            'palette': '팔레트', 'reprint_receipt': '영수증 재인쇄', 'card_payment': '카드 결제',
            'update_config': '설정 업데이트', 'redeem_points': '포인트 적립', 'print_label': '라벨 인쇄',
            'track_pour': '따르기 추적', 'move_crypto': '크립토 이동', 'fetch_orders': '온라인 주문 가져오기',
            'pay': '지불', 'subtotal': '소계', 'tax': '세금', 'total': '총계',
            'change': '거스름돈', 'welcome': '환영', 'thank_you': '감사합니다!',
            'item_correct': '품목 수정', 'return_merchandise': '상품 반품', 'multiplier': '승수',
            'bag_fee': '봉투 요금', 'atm_fee': 'ATM 요금', 'scale': '저울', 'tare': '용기 중량', 'apply_tare': '용기 중량 적용'
        },
        'Arabic': {
            'product_code': 'رمز المنتج', 'quantity': 'الكمية', 'price': 'السعر',
            'add_product': 'إضافة منتج', 'discount': 'خصم (%)', 'surcharge': 'رسوم إضافية ($)',
            'payment_method': 'طريقة الدفع', 'refund': 'استرداد', 'void': 'إلغاء',
            'exchange': 'تبادل', 'cancel': 'إلغاء المعاملة', 'generate_report': 'إنشاء تقرير',
            'login': 'تسجيل الدخول', 'logout': 'تسجيل الخروج', 'hold': 'تعليق', 'recall': 'استدعاء',
            'split_check': 'تقسيم الفاتورة', 'split_tender': 'تقسيم الدفع', 'convert': 'تحويل العملات',
            'qr_code': 'رمز QR', 'crypto_tax': 'تقرير ضرائب العملات المشفرة', 'reward_customer': 'مكافأة العميل',
            'ai_pricing': 'اقتراحات أسعار AI', 'multi_store': 'تحليل المتاجر المتعددة', 'hand_mode': 'الوضع اليدوي',
            'palette': 'لوحة الألوان', 'reprint_receipt': 'إعادة طباعة إيصال', 'card_payment': 'الدفع بالبطاقة',
            'update_config': 'تحديث التكوين', 'redeem_points': 'استبدال النقاط', 'print_label': 'طباعة ملصق',
            'track_pour': 'تتبع الصب', 'move_crypto': 'نقل العملات المشفرة', 'fetch_orders': 'جلب الطلبات عبر الإنترنت',
            'pay': 'دفع', 'subtotal': 'المجموع الفرعي', 'tax': 'الضريبة', 'total': 'الإجمالي',
            'change': 'الباقي', 'welcome': 'أهلاً بك', 'thank_you': 'شكراً لك!',
            'item_correct': 'تصحيح العنصر', 'return_merchandise': 'إرجاع البضاعة', 'multiplier': 'المضاعف',
            'bag_fee': 'رسوم الحقيبة', 'atm_fee': 'رسوم أجهزة الصراف', 'scale': 'الميزان', 'tare': 'الوزن الفارغ', 'apply_tare': 'تطبيق الوزن الفارغ'
        },
        'Hindi': {
            'product_code': 'उत्पाद कोड', 'quantity': 'मात्रा', 'price': 'कीमत',
            'add_product': 'उत्पाद जोड़ें', 'discount': 'छूट (%)', 'surcharge': 'अतिरिक्त शुल्क ($)',
            'payment_method': 'भुगतान विधि', 'refund': 'रिफंड', 'void': 'रद्द करें',
            'exchange': 'विनिमय', 'cancel': 'लेनदेन रद्द करें', 'generate_report': 'रिपोर्ट बनाएं',
            'login': 'लॉग इन', 'logout': 'लॉग आउट', 'hold': 'होल्ड', 'recall': 'याद करें',
            'split_check': 'बिल विभाजित करें', 'split_tender': 'भुगतान विभाजित करें', 'convert': 'मुद्रा परिवर्तन',
            'qr_code': 'QR कोड', 'crypto_tax': 'क्रिप्टो कर रिपोर्ट', 'reward_customer': 'ग्राहक को पुरस्कृत करें',
            'ai_pricing': 'AI मूल्य सुझाव', 'multi_store': 'मल्टी-स्टोर विश्लेषण', 'hand_mode': 'हैंड मोड',
            'palette': 'पैलेट', 'reprint_receipt': 'रसीद पुनः प्रिंट करें', 'card_payment': 'कार्ड भुगतान',
            'update_config': 'कॉन्फ़िगरेशन अपडेट करें', 'redeem_points': 'अंक भुनाएं', 'print_label': 'लेबल प्रिंट करें',
            'track_pour': 'पोर ट्रैक करें', 'move_crypto': 'क्रिप्टो स्थानांतरित करें', 'fetch_orders': 'ऑनलाइन ऑर्डर लाएं',
            'pay': 'भुगतान करें', 'subtotal': 'उप-योग', 'tax': 'कर', 'total': 'कुल',
            'change': 'बदलाव', 'welcome': 'स्वागत है', 'thank_you': 'धन्यवाद!',
            'item_correct': 'आइटम सुधार', 'return_merchandise': 'माल वापसी', 'multiplier': 'गुणक',
            'bag_fee': 'बैग शुल्क', 'atm_fee': 'ATM शुल्क', 'scale': 'पैमाना', 'tare': 'तार', 'apply_tare': 'तार लागू करें'
        }
    }
    
    # Currency Exchange Rates (base: USD) - 17 currencies from v1.0.1.6
    EXCHANGE_RATES = {
        'USD': 1.0,
        'EUR': 0.92,
        'GBP': 0.79,
        'BTC': 0.000010,
        'USDC': 1.0,
        'USDT': 1.0,
        'KRW': 1320.0,
        'JPY': 150.0,
        'TRY': 32.0,
        'ALL': 95.0,
        'CAD': 1.36,
        'AUD': 1.53,
        'CHF': 0.88,
        'CNY': 7.24,
        'INR': 83.0,
        'MXN': 17.15,
        'BRL': 4.97
    }
    
    CURRENCY_SYMBOLS = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'BTC': '₿', 'USDC': '$', 'USDT': '$',
        'KRW': '₩', 'JPY': '¥', 'TRY': '₺', 'ALL': 'L', 'CAD': 'C$', 'AUD': 'A$',
        'CHF': 'Fr', 'CNY': '¥', 'INR': '₹', 'MXN': '$', 'BRL': 'R$'
    }


# ==================== DATA CLASSES ====================

@dataclass
class Product:
    code: str
    name: str
    price: float
    quantity: int
    department: str = "General"
    tax_rates: List[str] = None
    track_inventory: bool = True
    open_price: bool = False
    plu_code: str = None
    crv_applicable: bool = False
    crv_rate: float = 0.0
    
    def __post_init__(self):
        if self.tax_rates is None:
            self.tax_rates = ['Berkeley']


@dataclass
class TransactionItem:
    plu_code: str
    name: str
    quantity: float
    unit_price: float
    tax_rate: float
    tax_amount: float
    crv_amount: float
    total: float
    voided: bool = False
    discount: float = 0.0


@dataclass
class Transaction:
    id: str
    clerk_id: str
    clerk_name: str
    start_time: datetime.datetime
    items: List[TransactionItem]
    payments: List[Dict]
    subtotal: float
    tax_total: float
    crv_total: float
    discounts: float
    surcharges: float
    total: float
    status: str
    mode: str
    end_time: datetime.datetime = None
    change: float = 0.0


# ==================== DATABASE ====================

class DatabaseManager:
    def __init__(self, db_path: str = "reggistarr.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER DEFAULT 0,
                department TEXT DEFAULT 'General',
                tax_rates TEXT DEFAULT '["Berkeley"]',
                track_inventory INTEGER DEFAULT 1,
                open_price INTEGER DEFAULT 0,
                plu_code TEXT,
                crv_applicable INTEGER DEFAULT 0,
                crv_rate REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                clerk_id TEXT NOT NULL,
                clerk_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                items TEXT NOT NULL,
                payments TEXT NOT NULL,
                subtotal REAL NOT NULL,
                tax_total REAL NOT NULL,
                crv_total REAL DEFAULT 0,
                discounts REAL DEFAULT 0,
                surcharges REAL DEFAULT 0,
                total REAL NOT NULL,
                status TEXT NOT NULL,
                mode TEXT NOT NULL,
                change REAL DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clerks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                pin TEXT NOT NULL,
                permissions TEXT NOT NULL,
                active INTEGER DEFAULT 0,
                total_sales REAL DEFAULT 0,
                transaction_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()


# ==================== CASH REGISTER CORE ====================

class CashRegister:
    def __init__(self):
        self.db = DatabaseManager()
        self.products: Dict[str, Product] = {}
        self.clerks: Dict[str, dict] = {}
        self.current_transaction: Optional[Transaction] = None
        self.current_clerk: Optional[dict] = None
        self.mode = "Register"
        self.load_data()
        self.init_sample_data()
        
        # TEC MA-79 Functions
        self.functions = {
            'Feed': self.feed,
            'Item Correct': self.item_correct,
            'Return': self.return_merchandise,
            'Multiplier': self.multiplier,
            'PLU': self.plu_lookup,
            'No Sale': self.no_sale,
            'Tax Mod': self.tax_modifier,
            'Discount': self.discount,
            'Bag Fee': self.bag_fee,
            'ATM Fee': self.atm_fee,
            'RA': self.received_on_account,
            'PO': self.paid_out,
            'Price Inquiry': self.price_inquiry,
            'Price Change': self.price_change,
            'Subtotal': self.show_subtotal,
            'Total': self.show_total,
            'CRV': self.bottle_fee,
            'Clear': self.clear_entry,
            'Enter': self.enter_item,
        }
    
    def load_data(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM products')
        for row in cursor.fetchall():
            self.products[row[0]] = Product(
                code=row[0], name=row[1], price=row[2], quantity=row[3],
                department=row[4], tax_rates=json.loads(row[5]),
                track_inventory=bool(row[6]), open_price=bool(row[7]),
                plu_code=row[8], crv_applicable=bool(row[9]), crv_rate=row[10]
            )
        
        cursor.execute('SELECT * FROM clerks')
        for row in cursor.fetchall():
            self.clerks[row[0]] = {
                'id': row[0], 'name': row[1], 'pin': row[2],
                'permissions': json.loads(row[3]), 'active': bool(row[4]),
                'total_sales': row[5], 'transaction_count': row[6]
            }
        
        conn.close()
    
    def init_sample_data(self):
        if not self.products:
            samples = [
                Product("1001", "Apple", 0.50, 100, "Produce", ["Berkeley"]),
                Product("1002", "Banana", 0.30, 150, "Produce", ["Berkeley"]),
                Product("1003", "Soda (12pk)", 5.99, 40, "Beverages", ["Berkeley"], crv_applicable=True, crv_rate=0.10),
                Product("1004", "Vape Kit", 29.99, 20, "Vape", ["Berkeley", "VapeTax"]),
                Product("1005", "E-Liquid", 14.99, 35, "Vape", ["Berkeley", "VapeTax"]),
                Product("1006", "Water Bottle", 1.29, 60, "Beverages", ["Berkeley"], crv_applicable=True, crv_rate=0.05),
                Product("1007", "Repair Service", 25.00, 999, "Services", [], open_price=True),
            ]
            for p in samples:
                self.add_product(p)
        
        if not self.clerks:
            self.add_clerk({'id': '001', 'name': 'Demo Clerk', 'pin': '1234',
                          'permissions': ['sale', 'refund', 'void', 'discount']})
    
    def add_product(self, product: Product):
        self.products[product.code] = product
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product.code, product.name, product.price, product.quantity,
              product.department, json.dumps(product.tax_rates),
              int(product.track_inventory), int(product.open_price),
              product.plu_code, int(product.crv_applicable), product.crv_rate))
        conn.commit()
        conn.close()
    
    def add_clerk(self, clerk: dict):
        self.clerks[clerk['id']] = clerk
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO clerks VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (clerk['id'], clerk['name'], clerk['pin'], json.dumps(clerk['permissions']),
              int(clerk.get('active', False)), clerk.get('total_sales', 0),
              clerk.get('transaction_count', 0)))
        conn.commit()
        conn.close()
    
    def login_clerk(self, clerk_id: str, pin: str) -> bool:
        clerk = self.clerks.get(clerk_id)
        if clerk and clerk['pin'] == pin:
            clerk['active'] = True
            self.current_clerk = clerk
            return True
        return False
    
    def calculate_tax(self, amount: float, tax_rates: List[str]) -> Tuple[float, Dict]:
        total_tax = 0.0
        breakdown = {}
        for rate_name in tax_rates:
            rate = Config.TAX_RATES.get(rate_name, 0.0)
            tax = amount * rate
            total_tax += tax
            breakdown[rate_name] = {'rate': rate, 'amount': tax}
        return total_tax, breakdown
    
    def start_transaction(self) -> Optional[Transaction]:
        if not self.current_clerk:
            return None
        
        txn_id = f"TXN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{id(self) % 10000}"
        self.current_transaction = Transaction(
            id=txn_id,
            clerk_id=self.current_clerk['id'],
            clerk_name=self.current_clerk['name'],
            start_time=datetime.datetime.now(),
            items=[],
            payments=[],
            subtotal=0.0,
            tax_total=0.0,
            crv_total=0.0,
            discounts=0.0,
            surcharges=0.0,
            total=0.0,
            status='open',
            mode=self.mode
        )
        return self.current_transaction
    
    def add_item(self, plu_code: str, quantity: float = 1.0, 
                 override_price: Optional[float] = None) -> Tuple[bool, str]:
        if not self.current_transaction or self.current_transaction.status != 'open':
            return False, "No active transaction"
        
        product = self.products.get(plu_code)
        if not product:
            return False, f"Product not found: {plu_code}"
        
        price = override_price if override_price is not None else product.price
        if override_price and not product.open_price:
            return False, "Price override not allowed"
        
        if product.track_inventory and product.quantity < quantity:
            return False, f"Insufficient stock: {product.quantity} available"
        
        item_subtotal = price * quantity
        tax_amount, _ = self.calculate_tax(item_subtotal, product.tax_rates)
        crv_amount = product.crv_rate * quantity if product.crv_applicable else 0.0
        
        item = TransactionItem(
            plu_code=plu_code,
            name=product.name,
            quantity=quantity,
            unit_price=price,
            tax_rate=sum(Config.TAX_RATES.get(r, 0) for r in product.tax_rates),
            tax_amount=tax_amount,
            crv_amount=crv_amount,
            total=item_subtotal + tax_amount + crv_amount
        )
        
        self.current_transaction.items.append(item)
        self.recalculate_transaction()
        
        if product.track_inventory:
            product.quantity -= int(quantity)
            self.add_product(product)
        
        return True, f"Added: {product.name} x{quantity}"
    
    def recalculate_transaction(self):
        if not self.current_transaction:
            return
        
        subtotal = 0.0
        tax = 0.0
        crv = 0.0
        
        for item in self.current_transaction.items:
            if not item.voided:
                subtotal += item.unit_price * item.quantity
                tax += item.tax_amount
                crv += item.crv_amount
        
        self.current_transaction.subtotal = subtotal
        self.current_transaction.tax_total = tax
        self.current_transaction.crv_total = crv
        self.current_transaction.total = (subtotal + tax + crv - 
                                          self.current_transaction.discounts + 
                                          self.current_transaction.surcharges)
    
    def void_item(self, index: int) -> bool:
        if not self.current_transaction or index >= len(self.current_transaction.items):
            return False
        
        item = self.current_transaction.items[index]
        item.voided = True
        
        product = self.products.get(item.plu_code)
        if product and product.track_inventory:
            product.quantity += int(item.quantity)
            self.add_product(product)
        
        self.recalculate_transaction()
        return True
    
    def add_payment(self, method: str, amount: float) -> Tuple[bool, float]:
        if not self.current_transaction:
            return False, 0.0
        
        payment = {'method': method, 'amount': amount, 
                  'timestamp': datetime.datetime.now().isoformat()}
        self.current_transaction.payments.append(payment)
        
        total_paid = sum(p['amount'] for p in self.current_transaction.payments)
        remaining = self.current_transaction.total - total_paid
        
        if remaining <= 0:
            self.current_transaction.change = abs(remaining)
            self.complete_transaction()
        
        return True, remaining
    
    def set_mode(self, mode: str) -> bool:
        """Set TEC MA-79 operating mode"""
        if mode in Config.MODES:
            self.mode = mode
            return True
        return False
    
    def generate_group_report(self) -> str:
        """Generate sales report by department/group"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT items FROM transactions WHERE status = 'completed'
        ''')
        
        group_sales = defaultdict(float)
        for row in cursor.fetchall():
            items = json.loads(row[0])
            for item in items:
                if not item.get('voided', False):
                    # Get department from product
                    product = self.products.get(item.get('plu_code', ''))
                    dept = product.department if product else 'Unknown'
                    group_sales[dept] += item.get('total', 0)
        
        conn.close()
        
        report_lines = ["Group/Department Sales Report", "=" * 40]
        for dept, total in sorted(group_sales.items(), key=lambda x: x[1], reverse=True):
            report_lines.append(f"{dept:20s} ${total:10.2f}")
        
        return "\n".join(report_lines)
    
    def generate_plu_report(self) -> str:
        """Generate sales report by PLU"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT items FROM transactions WHERE status = 'completed'
        ''')
        
        plu_sales = defaultdict(lambda: {'quantity': 0, 'total': 0.0})
        for row in cursor.fetchall():
            items = json.loads(row[0])
            for item in items:
                if not item.get('voided', False):
                    plu = item.get('plu_code', 'Unknown')
                    plu_sales[plu]['quantity'] += item.get('quantity', 0)
                    plu_sales[plu]['total'] += item.get('total', 0)
        
        conn.close()
        
        report_lines = ["PLU Sales Report", "=" * 50]
        report_lines.append(f"{'PLU':10s} {'Name':20s} {'Qty':>8s} {'Total':>10s}")
        report_lines.append("-" * 50)
        
        for plu, data in sorted(plu_sales.items(), key=lambda x: x[1]['total'], reverse=True):
            product = self.products.get(plu)
            name = product.name if product else 'Unknown'
            report_lines.append(f"{plu:10s} {name[:20]:20s} {data['quantity']:8.1f} ${data['total']:9.2f}")
        
        return "\n".join(report_lines)
    
    def generate_period_report(self, period_type: str = 'hourly') -> str:
        """Generate sales report by time period"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT start_time, total FROM transactions WHERE status = 'completed'
        ''')
        
        period_sales = defaultdict(float)
        for row in cursor.fetchall():
            timestamp = datetime.datetime.fromisoformat(row[0])
            total = row[1]
            
            if period_type == 'hourly':
                key = timestamp.strftime('%H:00')
            elif period_type == 'daily':
                key = timestamp.strftime('%Y-%m-%d')
            elif period_type == 'weekly':
                key = timestamp.strftime('%Y-W%W')
            elif period_type == 'monthly':
                key = timestamp.strftime('%Y-%m')
            else:
                key = timestamp.strftime('%Y-%m-%d %H:00')
            
            period_sales[key] += total
        
        conn.close()
        
        report_lines = [f"{period_type.capitalize()} Sales Report", "=" * 40]
        for period, total in sorted(period_sales.items()):
            report_lines.append(f"{period:20s} ${total:10.2f}")
        
        return "\n".join(report_lines)
    
    def generate_sales_totals(self, periods: List[str] = None) -> str:
        """Generate sales totals for multiple time periods"""
        if periods is None:
            periods = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
        
        now = datetime.datetime.now()
        period_deltas = {
            '1 day': datetime.timedelta(days=1),
            '1 week': datetime.timedelta(weeks=1),
            '3 weeks': datetime.timedelta(weeks=3),
            '1 month': datetime.timedelta(days=30),
            '3 months': datetime.timedelta(days=90),
            '6 months': datetime.timedelta(days=180),
            '1 year': datetime.timedelta(days=365),
        }
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        report_lines = ["Sales Totals Report", "=" * 40]
        
        for period in periods:
            delta = period_deltas.get(period, datetime.timedelta(days=1))
            start_date = now - delta
            
            cursor.execute('''
                SELECT SUM(total), COUNT(*) FROM transactions 
                WHERE start_time >= ? AND status = 'completed'
            ''', (start_date.isoformat(),))
            
            row = cursor.fetchone()
            total_sales = row[0] if row[0] else 0.0
            count = row[1] if row[1] else 0
            
            report_lines.append(f"{period:15s} ${total_sales:10.2f} ({count} transactions)")
        
        conn.close()
        return "\n".join(report_lines)
    
    def complete_transaction(self):
        if not self.current_transaction:
            return
        
        self.current_transaction.status = 'completed'
        self.current_transaction.end_time = datetime.datetime.now()
        
        if self.current_clerk:
            self.current_clerk['total_sales'] += self.current_transaction.total
            self.current_clerk['transaction_count'] += 1
            self.add_clerk(self.current_clerk)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (self.current_transaction.id, self.current_transaction.clerk_id,
              self.current_transaction.clerk_name,
              self.current_transaction.start_time.isoformat(),
              self.current_transaction.end_time.isoformat(),
              json.dumps([asdict(item) for item in self.current_transaction.items]),
              json.dumps(self.current_transaction.payments),
              self.current_transaction.subtotal, self.current_transaction.tax_total,
              self.current_transaction.crv_total, self.current_transaction.discounts,
              self.current_transaction.surcharges, self.current_transaction.total,
              self.current_transaction.status, self.current_transaction.mode,
              self.current_transaction.change))
        conn.commit()
        conn.close()
    
    # TEC MA-79 Function Implementations
    def feed(self): pass
    
    def item_correct(self):
        """Item Correct - Void the last item entered"""
        if not self.current_transaction or len(self.current_transaction.items) == 0:
            return "No items to correct"
        
        # Void the last item
        last_index = len(self.current_transaction.items) - 1
        result = self.register.void_item(last_index)
        
        if result:
            return f"Item corrected (voided)"
        return "Failed to correct item"
    
    def return_merchandise(self):
        """Return Merchandise - Process a return"""
        # Opens a return dialog or starts return mode
        # For now, add a negative quantity item
        if not self.current_transaction:
            return "No transaction"
        return "Return mode - enter item with negative qty or use refund"
    
    def multiplier(self):
        """Multiplier - Set quantity multiplier for next item"""
        # This would typically be used with keypad input
        return "Multiplier mode - enter qty then item"
    
    def plu_lookup(self):
        """PLU Lookup - Search for product by code"""
        return "PLU Lookup - enter product code"
    def no_sale(self):
        """No Sale - Open drawer and ring bell"""
        result = "Drawer opened"
        
        # Ring the bell (for attention)
        self.ring_bell(pattern="no_sale")
        
        return result
    
    def ring_bell(self, pattern: str = "short"):
        """Ring the POS bell
        Patterns: short, long, double, triple, no_sale, alert, error
        """
        try:
            if sys.platform == "win32":
                import winsound
                if pattern == "no_sale":
                    winsound.MessageBeep(winsound.MB_OK)
                elif pattern == "error":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                else:
                    winsound.Beep(1000, 200)
            else:
                # Linux/macOS - use beep or aplay
                import subprocess
                freq = 1000
                duration = 200
                count = 1
                
                if pattern == "no_sale":
                    count = 2
                    duration = 150
                elif pattern == "double":
                    count = 2
                elif pattern == "triple":
                    count = 3
                elif pattern == "error":
                    freq = 500
                    duration = 300
                    count = 3
                
                for _ in range(count):
                    try:
                        subprocess.run(['beep', '-f', str(freq), '-l', str(duration)], 
                                    capture_output=True, timeout=1)
                    except FileNotFoundError:
                        # beep not installed, try speaker
                        try:
                            subprocess.run(['paplay', '/usr/share/sounds/gtk-events/click.wav'],
                                        capture_output=True, timeout=1)
                        except:
                            pass  # No sound available
                    if count > 1:
                        import time
                        time.sleep(0.15)
        except Exception as e:
            pass  # Silently fail if no sound
    def tax_modifier(self):
        """Tax Modifier - Change tax rate for current item"""
        # Opens dialog to select tax-exempt or different tax rate
        return "Tax modifier - select rate for item"
    
    def discount(self):
        """Apply 10% discount to transaction"""
        if not self.current_transaction:
            return "No transaction"
        
        # Apply 10% discount
        result = self.register.apply_discount(10.0, percentage=True)
        if result:
            self.ring_bell("short")  # Feedback beep
            return f"10% Discount applied"
        return "Failed to apply discount"
    
    def bag_fee(self):
        """Add bag fee to transaction"""
        if not self.current_transaction:
            return "No transaction"
        
        bag_fee = 0.10  # 10 cents per bag
        result = self.register.apply_surcharge(bag_fee, "Bag Fee")
        if result:
            return f"Bag fee (${bag_fee:.2f}) added"
        return "Failed to add bag fee"
    
    def atm_fee(self):
        """Add ATM fee to transaction"""
        if not self.current_transaction:
            return "No transaction"
        
        fee = 3.00  # $3 ATM fee
        result = self.register.apply_surcharge(fee, "ATM Fee")
        if result:
            return f"ATM fee (${fee:.2f}) added"
        return "Failed to add ATM fee"
    
    def received_on_account(self):
        """Received on Account - Record payment toward account"""
        return "Received on account - enter amount and customer"
    
    def paid_out(self):
        """Paid Out - Record cash paid out"""
        return "Paid out - enter amount and reason"
    
    def price_inquiry(self, plu_code: str) -> str:
        product = self.products.get(plu_code)
        if product:
            return f"{product.name}: {Config.CURRENCY_SYMBOL}{product.price:.2f}"
        return "Product not found"
    
    def price_change(self):
        """Price Change - Override item price"""
        return "Price change - enter new price for item"
    
    def bottle_fee(self):
        """Add CRV/bottle deposit fee"""
        if not self.current_transaction:
            return "No transaction"
        
        # California CRV is $0.05/$0.10
        crv = 0.10
        result = self.register.apply_surcharge(crv, "CRV/Bottle Deposit")
        if result:
            return f"CRV (${crv:.2f}) added"
        return "Failed to add CRV"
    
    def clear_entry(self):
        """Clear current entry"""
        return "Entry cleared"
    
    def enter_item(self):
        """Enter item into transaction"""
        return "Item entered"
    
    # Extended Features
    def process_split_tender(self, payments: List[Tuple[str, float]]) -> bool:
        """Process multiple payment methods for one transaction"""
        if not self.current_transaction:
            return False
        
        total_paid = 0.0
        for method, amount in payments:
            total_paid += amount
            self.current_transaction.payments.append({
                'method': method,
                'amount': amount,
                'timestamp': datetime.datetime.now().isoformat()
            })
        
        if total_paid >= self.current_transaction.total:
            self.current_transaction.change = total_paid - self.current_transaction.total
            self.complete_transaction()
            return True
        return False
    
    def create_layaway(self, deposit: float, customer_id: str, due_date: datetime.datetime) -> str:
        """Create layaway transaction"""
        if not self.current_transaction:
            return ""
        
        layaway_id = f"LAYAWAY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS layaways (
                layaway_id TEXT PRIMARY KEY,
                transaction_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                deposit_amount REAL NOT NULL,
                balance_due REAL NOT NULL,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_date TEXT NOT NULL
            )
        ''')
        
        balance = self.current_transaction.total - deposit
        cursor.execute('''
            INSERT INTO layaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (layaway_id, self.current_transaction.id, customer_id,
              self.current_transaction.total, deposit, balance,
              due_date.isoformat(), 'active', datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        # Mark original transaction as layaway
        self.current_transaction.status = 'layaway'
        self.db.save_transaction(self.current_transaction)
        
        return layaway_id
    
    def process_layaway_payment(self, layaway_id: str, amount: float) -> Tuple[bool, float]:
        """Make payment on layaway"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT balance_due FROM layaways WHERE layaway_id = ?', (layaway_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, 0.0
        
        current_balance = row[0]
        new_balance = current_balance - amount
        
        if new_balance <= 0:
            cursor.execute('UPDATE layaways SET balance_due = 0, status = ? WHERE layaway_id = ?',
                         ('completed', layaway_id))
        else:
            cursor.execute('UPDATE layaways SET balance_due = ? WHERE layaway_id = ?',
                         (new_balance, layaway_id))
        
        conn.commit()
        conn.close()
        
        return True, new_balance
    
    def add_customer(self, customer_id: str, name: str, email: str = "", phone: str = "") -> bool:
        """Add customer to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_date TEXT NOT NULL,
                total_purchases REAL DEFAULT 0.0,
                visit_count INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, name, email, phone, datetime.datetime.now().isoformat(), 0.0, 0))
        conn.commit()
        conn.close()
        return True
    
    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers WHERE customer_id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'customer_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'created_date': row[4],
                'total_purchases': row[5],
                'visit_count': row[6]
            }
        return None
    
    def issue_gift_card(self, card_id: str, amount: float) -> bool:
        """Issue new gift card"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gift_cards (
                card_id TEXT PRIMARY KEY,
                initial_amount REAL NOT NULL,
                balance REAL NOT NULL,
                issue_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        expiry = datetime.datetime.now() + datetime.timedelta(days=365)
        cursor.execute('''
            INSERT INTO gift_cards VALUES (?, ?, ?, ?, ?, ?)
        ''', (card_id, amount, amount, datetime.datetime.now().isoformat(),
              expiry.isoformat(), 'active'))
        conn.commit()
        conn.close()
        return True
    
    def get_gift_card_balance(self, card_id: str) -> float:
        """Check gift card balance"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM gift_cards WHERE card_id = ? AND status = ?',
                      (card_id, 'active'))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0
    
    def redeem_gift_card(self, card_id: str, amount: float) -> bool:
        """Redeem amount from gift card"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT balance FROM gift_cards WHERE card_id = ? AND status = ?',
                      (card_id, 'active'))
        row = cursor.fetchone()
        
        if not row or row[0] < amount:
            conn.close()
            return False
        
        new_balance = row[0] - amount
        status = 'active' if new_balance > 0 else 'depleted'
        cursor.execute('UPDATE gift_cards SET balance = ?, status = ? WHERE card_id = ?',
                      (new_balance, status, card_id))
        conn.commit()
        conn.close()
        return True
    
    def generate_custom_report(self, start_date: datetime.datetime, 
                               end_date: datetime.datetime,
                               report_type: str = 'sales') -> str:
        """Generate custom date range report"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE start_time BETWEEN ? AND ? AND status = 'completed'
        ''', (start_date.isoformat(), end_date.isoformat()))
        
        transactions = cursor.fetchall()
        conn.close()
        
        total_sales = sum(t[11] for t in transactions)
        total_tax = sum(t[9] for t in transactions)
        
        report_lines = [
            f"Custom Report: {report_type}",
            f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            f"Total Transactions: {len(transactions)}",
            f"Total Sales: ${total_sales:.2f}",
            f"Total Tax: ${total_tax:.2f}",
            "=" * 50,
        ]
        
        return "\n".join(report_lines)
    
    # Advanced Features
    def hold_transaction(self) -> str:
        """Hold current transaction for later recall"""
        if not self.current_transaction:
            return ""
        
        hold_id = f"HOLD-{datetime.datetime.now().strftime('%H%M%S')}"
        self.current_transaction.status = 'held'
        
        # Save to held transactions table
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS held_transactions (
                hold_id TEXT PRIMARY KEY,
                transaction_data TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                clerk_id TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            INSERT INTO held_transactions VALUES (?, ?, ?, ?)
        ''', (hold_id, json.dumps(asdict(self.current_transaction)),
              datetime.datetime.now().isoformat(),
              self.current_clerk['id'] if self.current_clerk else 'unknown'))
        conn.commit()
        conn.close()
        
        self.current_transaction = None
        return hold_id
    
    def recall_transaction(self, hold_id: str) -> bool:
        """Recall a held transaction"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT transaction_data FROM held_transactions WHERE hold_id = ?', (hold_id,))
        row = cursor.fetchone()
        
        if row:
            data = json.loads(row[0])
            # Restore transaction (simplified - would need full reconstruction)
            cursor.execute('DELETE FROM held_transactions WHERE hold_id = ?', (hold_id,))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    
    def split_check(self, num_splits: int) -> List[float]:
        """Split current transaction into multiple checks"""
        if not self.current_transaction:
            return []
        
        total = self.current_transaction.total
        base_amount = total / num_splits
        splits = []
        
        for i in range(num_splits):
            if i == num_splits - 1:
                # Last split gets any rounding remainder
                split_amount = round(total - sum(splits), 2)
            else:
                split_amount = round(base_amount, 2)
            splits.append(split_amount)
        
        return splits
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between currencies"""
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first, then to target
        usd_amount = amount / Config.EXCHANGE_RATES.get(from_currency, 1.0)
        target_amount = usd_amount * Config.EXCHANGE_RATES.get(to_currency, 1.0)
        
        return round(target_amount, 8 if to_currency == 'BTC' else 2)
    
    def generate_payment_qr(self, amount: float, method: str = 'BTC') -> Optional[str]:
        """Generate QR code for payment"""
        if not QR_AVAILABLE:
            return None
        
        if method == 'BTC':
            # Bitcoin payment URI
            btc_amount = self.convert_currency(amount, 'USD', 'BTC')
            qr_data = f"bitcoin:1PerformanceSupplyDepot?amount={btc_amount}&message=Payment"
        else:
            # Generic payment data
            qr_data = f"PAYMENT|{Config.STORE_NAME}|{amount}|{method}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def update_exchange_rates(self):
        """Fetch latest exchange rates from API"""
        try:
            # Using exchangerate-api.com (free tier available)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                rates = data.get('rates', {})
                
                # Update Config rates
                Config.EXCHANGE_RATES['EUR'] = rates.get('EUR', 0.85)
                Config.EXCHANGE_RATES['GBP'] = rates.get('GBP', 0.75)
                Config.EXCHANGE_RATES['JPY'] = rates.get('JPY', 110.0)
                Config.EXCHANGE_RATES['CAD'] = rates.get('CAD', 1.25)
                Config.EXCHANGE_RATES['AUD'] = rates.get('AUD', 1.35)
                
                return True
        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            # Fallback to default rates
            return False


# ==================== GUI APPLICATION ====================

class ReggieStarrGUI:
    def __init__(self, master):
        self.master = master
        master.title(f"ReggieStarr v4.2 - {Config.STORE_NAME}")
        master.geometry("1024x768")
        master.configure(bg='#1a1a2e')
        
        self.register = CashRegister()
        self.input_buffer = ""
        self.last_function = None
        self.current_language = "English"
        self.current_currency = "USD"
        self.current_discount_pct = 0.0
        self.current_discount_fixed = 0.0
        self.current_multiplier = 1.0
        self.current_tare = 0.0
        
        self.create_styles()
        self.create_header()
        self.create_display()
        self.create_function_buttons()
        self.create_keypad()
        self.create_payment_buttons()
        
        # Show login dialog
        self.show_login_dialog()
    
    def create_styles(self):
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#1a1a2e')
        self.style.configure('Header.TLabel', background='#16213e', foreground='white', 
                           font=('Courier', 12, 'bold'))
        self.style.configure('Display.TLabel', background='#000000', foreground='#00FF00',
                           font=('Courier', 14))
    
    def create_header(self):
        header = ttk.Frame(self.master, style='TFrame')
        header.pack(fill='x', padx=5, pady=5)
        
        # Language selector
        lang_frame = ttk.Frame(header, style='TFrame')
        lang_frame.pack(side='left', padx=5)
        ttk.Label(lang_frame, text="Lang:", style='Header.TLabel').pack(side='left')
        self.lang_var = tk.StringVar(value='English')
        self.lang_menu = ttk.Combobox(lang_frame, textvariable=self.lang_var, 
                                      values=list(Config.LANGUAGES.keys()), 
                                      width=10, state='readonly')
        self.lang_menu.pack(side='left', padx=5)
        self.lang_menu.bind('<<ComboboxSelected>>', lambda e: self.on_language_change())
        
        # Currency selector
        curr_frame = ttk.Frame(header, style='TFrame')
        curr_frame.pack(side='left', padx=5)
        ttk.Label(curr_frame, text="Curr:", style='Header.TLabel').pack(side='left')
        self.curr_var = tk.StringVar(value='USD')
        self.curr_menu = ttk.Combobox(curr_frame, textvariable=self.curr_var,
                                      values=list(Config.EXCHANGE_RATES.keys()),
                                      width=8, state='readonly')
        self.curr_menu.pack(side='left', padx=5)
        self.curr_menu.bind('<<ComboboxSelected>>', lambda e: self.on_currency_change())
        
        self.lbl_mode = ttk.Label(header, text="MODE: REGISTER", style='Header.TLabel')
        self.lbl_mode.pack(side='left', padx=10)
        
        self.lbl_clerk = ttk.Label(header, text="CLERK: Not Logged In", style='Header.TLabel')
        self.lbl_clerk.pack(side='left', padx=10)
        
        self.lbl_time = ttk.Label(header, text="", style='Header.TLabel')
        self.lbl_time.pack(side='right', padx=10)
        self.update_clock()
        
        # F-Key bindings (from v1.0.1.6)
        self.master.bind('<F1>', lambda e: self.show_help())
        self.master.bind('<F2>', lambda e: self.show_login_dialog())
        self.master.bind('<F3>', lambda e: self.logout_clerk())
        self.master.bind('<F4>', lambda e: self.hold_transaction())
        self.master.bind('<F5>', lambda e: self.show_recall_dialog())
        self.master.bind('<F8>', lambda e: self.show_reports_dialog())
        self.master.bind('<F9>', lambda e: self.void_last_item())
        self.master.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.master.bind('<F12>', lambda e: self.cancel_transaction())
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        state = self.master.attributes('-fullscreen')
        self.master.attributes('-fullscreen', not state)
    
    def show_help(self):
        """Show help dialog (F1)"""
        help_text = """
REGSTARR KEYBOARD SHORTCUTS:

F1  - Help (this dialog)
F2  - Clerk Login
F3  - Clerk Logout
F4  - Hold Transaction
F5  - Recall Transaction
F8  - Generate Report
F9  - Void Last Item
F11 - Toggle Fullscreen
F12 - Cancel Transaction

@discount - Apply discount
@refund  - Process refund
@void    - Void item
@split   - Split check
@hold    - Hold transaction
@recall  - Recall transaction
"""
        messagebox.showinfo("Help - Keyboard Shortcuts", help_text)
    
    def logout_clerk(self):
        """Logout current clerk (F3)"""
        if self.register.current_clerk:
            message = f"Logging out clerk: {self.register.current_clerk.name}"
            self.register.current_clerk = None
            self.lbl_clerk.config(text="CLERK: Not Logged In")
            messagebox.showinfo("Logged Out", message)
        else:
            messagebox.showwarning("No Clerk", "No clerk is currently logged in")
    
    def hold_transaction(self):
        """Hold current transaction (F4)"""
        if self.register.current_transaction.items:
            self.register.hold_transaction()
            messagebox.showinfo("Held", "Transaction held successfully")
            self.register.start_new_transaction()
            self.update_display()
        else:
            messagebox.showwarning("Empty", "No items to hold")
    
    def void_last_item(self):
        """Void last item (F9)"""
        if self.register.current_transaction.items:
            self.register.void_last_item()
            self.update_display()
        else:
            messagebox.showwarning("Empty", "No items to void")
    
    def cancel_transaction(self):
        """Cancel current transaction (F12)"""
        if self.register.current_transaction.items:
            if messagebox.askyesno("Cancel", "Cancel current transaction?"):
                self.register.start_new_transaction()
                self.update_display()
                messagebox.showinfo("Cancelled", "Transaction cancelled")
        else:
            messagebox.showwarning("Empty", "Transaction is already empty")
    
    def on_language_change(self):
        """Handle language change - update all UI labels"""
        lang = self.lang_var.get()
        self.current_language = lang
        # Update button labels that have translations
        self.update_button_labels()
        self.update_display(f"Language changed to: {lang}")
    
    def on_currency_change(self):
        """Handle currency change"""
        curr = self.curr_var.get()
        self.current_currency = curr
        symbol = Config.CURRENCY_SYMBOLS.get(curr, '$')
        self.update_display(f"Currency changed to: {curr} ({symbol})")
    
    def update_button_labels(self):
        """Update function button labels based on current language"""
        lang = getattr(self, 'current_language', 'English')
        labels = Config.LANGUAGES.get(lang, Config.LANGUAGES['English'])
        
        # Map function names to language keys
        mapping = {
            'Discount': labels.get('discount', 'Discount'),
            'Void Item': labels.get('void', 'Void'),
            'Currency': labels.get('convert', 'Currency'),
            'QR Pay': labels.get('qr_code', 'QR Pay'),
            'Refund': labels.get('refund', 'Refund'),
        }
        # Note: Full implementation would update all buttons
    
    def update_clock(self):
        self.lbl_time.config(text=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.master.after(1000, self.update_clock)
    
    def create_display(self):
        display_frame = ttk.Frame(self.master, style='TFrame')
        display_frame.pack(fill='x', padx=10, pady=5)
        
        self.txt_display = scrolledtext.ScrolledText(
            display_frame, height=15, width=80, font=('Courier', 12),
            bg='#000000', fg='#00FF00', insertbackground='#00FF00'
        )
        self.txt_display.pack(fill='both', expand=True)
        self.update_display()
    
    def create_function_buttons(self):
        func_frame = ttk.Frame(self.master, style='TFrame')
        func_frame.pack(fill='x', padx=10, pady=5)
        
        # Function buttons with @ prefix for quick keypad entry (from v1.0.1.6)
        functions = [
            ('PLU', '#4a4a6a'), ('QTY', '#4a4a6a'), ('Price Inquiry', '#4a4a6a'),
            ('Discount', '#6a4a4a'), ('Void Item', '#6a4a4a'), ('Void Txn', '#6a4a4a'),
            ('Subtotal', '#4a6a4a'), ('Total', '#2a6a2a'), ('No Sale', '#4a4a6a'),
            ('Bag Fee', '#4a4a6a'), ('CRV', '#4a4a6a'), ('Tax Exempt', '#4a4a6a'),
            ('Refund', '#8a4a4a'), ('Item Correct', '#6a6a8a'), ('Return', '#8a6a6a'),
            ('Add PLU', '#6a4a6a'), ('Dept Mgmt', '#6a4a6a'), ('Inventory', '#6a4a6a'),
            ('Hold', '#4a6a6a'), ('Recall', '#6a6a4a'), ('Split', '#6a4a6a'),
            ('Currency', '#4a4a8a'), ('QR Pay', '#8a4a8a'), ('Update Rates', '#4a8a4a'),
            ('Layaway', '#6a6a6a'), ('Gift Card', '#8a6a4a'), ('Customer', '#4a6a8a'),
            ('Mode', '#6a4a8a'), ('Reports', '#4a8a6a'), ('Z-Report', '#8a6a6a'),
            ('Scale', '#4a6a6a'), ('Tare', '#6a6a6a'), ('ATM Fee', '#6a4a6a'),
        ]
        
        for i, (text, color) in enumerate(functions):
            btn = tk.Button(func_frame, text=text, bg=color, fg='white',
                          font=('Arial', 10, 'bold'), width=12, height=2,
                          command=lambda t=text: self.handle_function(t))
            btn.grid(row=i//4, column=i%4, padx=3, pady=3, sticky='nsew')
    
    def create_keypad(self):
        keypad_frame = ttk.Frame(self.master, style='TFrame')
        keypad_frame.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        
        keys = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['C', '0', '00'],
        ]
        
        for row_idx, row in enumerate(keys):
            for col_idx, key in enumerate(row):
                btn = tk.Button(keypad_frame, text=key, bg='#666666', fg='white',
                              font=('Arial', 16, 'bold'), width=8, height=3,
                              command=lambda k=key: self.handle_keypad(k))
                btn.grid(row=row_idx, column=col_idx, padx=3, pady=3, sticky='nsew')
        
        # Enter button
        btn_enter = tk.Button(keypad_frame, text='ENTER', bg='#0066CC', fg='white',
                             font=('Arial', 16, 'bold'), width=8, height=3,
                             command=self.handle_enter)
        btn_enter.grid(row=4, column=0, columnspan=3, padx=3, pady=3, sticky='nsew')
    
    def create_payment_buttons(self):
        payment_frame = ttk.Frame(self.master, style='TFrame')
        payment_frame.pack(side='right', fill='y', padx=10, pady=5)
        
        ttk.Label(payment_frame, text="PAYMENT", style='Header.TLabel').pack(pady=5)
        
        for method in Config.PAYMENT_METHODS[:6]:  # Show first 6
            btn = tk.Button(payment_frame, text=method, bg='#2a6a2a', fg='white',
                          font=('Arial', 12), width=15, height=2,
                          command=lambda m=method: self.handle_payment(m))
            btn.pack(pady=2, fill='x')
    
    def show_login_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Clerk Login")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Clerk ID:").pack(pady=5)
        entry_id = ttk.Entry(dialog)
        entry_id.pack(pady=5)
        entry_id.insert(0, "001")
        
        ttk.Label(dialog, text="PIN:").pack(pady=5)
        entry_pin = ttk.Entry(dialog, show="*")
        entry_pin.pack(pady=5)
        entry_pin.insert(0, "1234")
        
        def do_login():
            if self.register.login_clerk(entry_id.get(), entry_pin.get()):
                self.lbl_clerk.config(text=f"CLERK: {self.register.current_clerk['name']}")
                self.register.start_transaction()
                dialog.destroy()
                self.update_display()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        
        ttk.Button(dialog, text="Login", command=do_login).pack(pady=10)
        entry_pin.bind('<Return>', lambda e: do_login())
        entry_id.focus()
    
    def handle_keypad(self, key):
        if key == 'C':
            self.input_buffer = ""
        else:
            self.input_buffer += key
        self.update_display()
    
    def handle_enter(self):
        if not self.input_buffer:
            return
            
        # Handle @ functions (quick access from v1.0.1.6)
        if self.input_buffer.startswith('@'):
            cmd = self.input_buffer[1:].lower()
            if cmd == 'discount' or cmd == '@discount':
                self.show_discount_dialog()
            elif cmd == 'refund' or cmd == '@refund':
                self.show_refund_dialog()
            elif cmd == 'item_correct' or cmd == 'correct':
                self.show_item_correction_dialog()
            elif cmd == 'return' or cmd == 'return_merchandise':
                self.show_return_dialog()
            elif cmd == 'multiplier':
                self.show_multiplier_dialog()
            elif cmd == 'bag_fee' or cmd == 'bag':
                self.add_bag_fee()
            elif cmd == 'atm_fee' or cmd == 'atm':
                self.add_atm_fee()
            elif cmd == 'scale' or cmd == 'tare':
                self.show_scale_dialog()
            elif cmd == 'void':
                self.handle_function("Void Item")
            elif cmd == 'voidall':
                self.handle_function("Void Txn")
            elif cmd == 'subtotal':
                self.handle_function("Subtotal")
            elif cmd == 'total':
                self.handle_function("Total")
            else:
                messagebox.showerror("Unknown Command", f"@{cmd} not recognized")
            self.input_buffer = ""
            self.update_display()
            return
        
        # Normal PLU entry
        if self.register.current_transaction:
            success, msg = self.register.add_item(self.input_buffer, 1)
            if success:
                self.input_buffer = ""
            else:
                messagebox.showerror("Error", msg)
        self.update_display()
    
    def show_multiplier_dialog(self):
        """Dialog for quantity multiplier"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Multiplier")
        dialog.geometry("250x150")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter multiplier:").pack(pady=10)
        mult_entry = ttk.Entry(dialog, font=('Arial', 16), width=10, justify='center')
        mult_entry.pack(pady=10)
        mult_entry.insert(0, "1")
        mult_entry.select_range(0, 'end')
        mult_entry.focus()
        
        def apply_mult():
            try:
                mult = float(mult_entry.get())
                if mult > 0:
                    self.current_multiplier = mult
                    self.update_display(f"Multiplier set: x{mult}")
                    dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid multiplier")
        
        ttk.Button(dialog, text="Apply", command=apply_mult).pack(pady=10)
        dialog.bind('<Return>', lambda e: apply_mult())
    
    def handle_function(self, func):
        if func == "Price Inquiry":
            if self.input_buffer:
                result = self.register.functions['Price Inquiry'](self.input_buffer)
                messagebox.showinfo("Price Inquiry", result)
        elif func == "Void Item":
            if self.input_buffer:
                try:
                    idx = int(self.input_buffer) - 1
                    if self.register.void_item(idx):
                        self.input_buffer = ""
                except ValueError:
                    pass
        elif func == "Void Txn":
            if messagebox.askyesno("Confirm", "Void entire transaction?"):
                self.register.current_transaction = None
                self.register.start_transaction()
                self.input_buffer = ""
        elif func == "Subtotal":
            pass
        elif func == "Total":
            pass
        elif func == "No Sale":
            result = self.register.functions['No Sale']()
            messagebox.showinfo("No Sale", result)
        elif func == "Add PLU":
            self.show_add_plu_dialog()
        elif func == "Dept Mgmt":
            self.show_department_dialog()
        elif func == "Inventory":
            self.show_inventory_dialog()
        elif func == "Hold":
            hold_id = self.register.hold_transaction()
            if hold_id:
                messagebox.showinfo("Transaction Held", f"Hold ID: {hold_id}")
                self.register.start_transaction()
            self.update_display()
        elif func == "Recall":
            self.show_recall_dialog()
        elif func == "Split":
            self.show_split_dialog()
        elif func == "Currency":
            self.show_currency_dialog()
        elif func == "QR Pay":
            self.show_qr_dialog()
        elif func == "Update Rates":
            success = self.register.update_exchange_rates()
            if success:
                messagebox.showinfo("Success", "Exchange rates updated!")
            else:
                messagebox.showwarning("Warning", "Using default rates (API unavailable)")
        elif func == "Layaway":
            self.show_layaway_dialog()
        elif func == "Gift Card":
            self.show_gift_card_dialog()
        elif func == "Customer":
            self.show_customer_dialog()
        elif func == "Mode":
            self.show_mode_dialog()
        elif func == "Reports":
            self.show_reports_dialog()
        elif func == "Z-Report":
            self.generate_z_report()
        elif func == "Discount":
            self.show_discount_dialog()
        elif func == "Refund":
            self.show_refund_dialog()
        elif func == "Bag Fee":
            self.add_bag_fee()
        elif func == "CRV":
            self.add_crv_fee()
        elif func == "Refund":
            self.show_refund_dialog()
        elif func == "Item Correct":
            self.show_item_correction_dialog()
        elif func == "Return":
            self.show_return_dialog()
        elif func == "Scale":
            self.show_scale_dialog()
        elif func == "Tare":
            self.show_tare_dialog()
        elif func == "ATM Fee":
            self.add_atm_fee()
        elif func == "Exchange":
            self.show_exchange_dialog()
        elif func == "Crypto Tax":
            self.show_crypto_tax_dialog()
        elif func == "Reward Customer":
            self.show_reward_customer_dialog()
        elif func == "AI Pricing":
            self.show_ai_pricing_dialog()
        elif func == "Multi-Store":
            self.show_multi_store_dialog()
    
    def show_exchange_dialog(self):
        """Dialog for item exchange - swap items or process returns with exchange"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Exchange / Return Exchange")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Exchange Items", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Current transaction items
        ttk.Label(dialog, text="Current Transaction Items:").pack(pady=5)
        
        items_frame = ttk.Frame(dialog)
        items_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create treeview for items
        cols = ('PLU', 'Name', 'Qty', 'Price', 'Total')
        tree = ttk.Treeview(items_frame, columns=cols, show='headings', height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Populate with current items
        for item in self.register.current_transaction.items:
            tree.insert('', 'end', values=(item.plu_code, item.name[:20], item.quantity, f"${item.unit_price:.2f}", f"${item.total:.2f}"))
        
        # Exchange options
        ttk.Label(dialog, text="Exchange Options:").pack(pady=10)
        
        options_frame = ttk.Frame(dialog)
        options_frame.pack(pady=5)
        
        ttk.Button(options_frame, text="Process Exchange", 
                  command=lambda: self._process_exchange(tree, dialog)).pack(side='left', padx=5)
        ttk.Button(options_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def _process_exchange(self, tree, dialog):
        """Process the exchange"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to exchange")
            return
        
        # Get selected item
        item_values = tree.item(selection[0])['values']
        messagebox.showinfo("Exchange", f"Exchange processed for item: {item_values[1]}")
        dialog.destroy()
    
    def show_crypto_tax_dialog(self):
        """Dialog for crypto tax report"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Crypto Tax Report")
        dialog.geometry("700x500")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Cryptocurrency Tax Report", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Date range
        date_frame = ttk.Frame(dialog)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        start_entry = ttk.Entry(date_frame, width=12)
        start_entry.grid(row=0, column=1, padx=5)
        start_entry.insert(0, "2025-01-01")
        
        ttk.Label(date_frame, text="End Date:").grid(row=0, column=2, padx=5)
        end_entry = ttk.Entry(date_frame, width=12)
        end_entry.grid(row=0, column=3, padx=5)
        from datetime import datetime
        end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Report display
        text = scrolledtext.ScrolledText(dialog, width=80, height=25)
        text.pack(padx=10, pady=10, fill='both', expand=True)
        
        def generate_report():
            text.delete('1.0', tk.END)
            report = self.register.generate_crypto_tax_report(start_entry.get(), end_entry.get())
            text.insert('1.0', report)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Generate Report", command=generate_report).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export CSV", command=lambda: self._export_crypto_csv(text.get('1.0', tk.END))).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side='left', padx=5)
        
        # Auto-generate on open
        generate_report()
    
    def _export_crypto_csv(self, content):
        """Export crypto tax report to CSV"""
        try:
            with open('crypto_tax_report.csv', 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", "Crypto tax report exported to crypto_tax_report.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export: {e}")
    
    def show_reward_customer_dialog(self):
        """Dialog for issuing BTC rewards to customers"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Reward Customer")
        dialog.geometry("400x350")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Issue Crypto Reward", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Customer selection
        ttk.Label(dialog, text="Customer:").pack(pady=5)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var, width=30)
        customer_combo['values'] = list(self.register.customers.keys()) if hasattr(self.register, 'customers') else ['Walk-in Customer']
        customer_combo.pack(pady=5)
        
        # Reward amount
        ttk.Label(dialog, text="Reward Amount (USD):").pack(pady=5)
        amount_entry = ttk.Entry(dialog, width=15)
        amount_entry.pack(pady=5)
        amount_entry.insert(0, "10.00")
        
        # Crypto selection
        ttk.Label(dialog, text="Cryptocurrency:").pack(pady=5)
        crypto_var = tk.StringVar(value="BTC")
        crypto_combo = ttk.Combobox(dialog, textvariable=crypto_var, values=['BTC', 'USDC', 'USDT'], width=10)
        crypto_combo.pack(pady=5)
        
        # Result
        result_label = ttk.Label(dialog, text="", font=('Courier', 10))
        result_label.pack(pady=10)
        
        def issue_reward():
            try:
                amount = float(amount_entry.get())
                customer = customer_var.get() or 'Walk-in Customer'
                crypto = crypto_var.get()
                
                # Calculate crypto amount (simplified)
                rates = {'BTC': 45000, 'USDC': 1, 'USDT': 1}
                crypto_amount = amount / rates.get(crypto, 1)
                
                result_label.config(text=f"Reward issued:\n{customer}\n{crypto_amount:.8f} {crypto}")
                messagebox.showinfo("Success", f"Reward issued: {crypto_amount:.8f} {crypto}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not issue reward: {e}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Issue Reward", command=issue_reward).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def show_ai_pricing_dialog(self):
        """Dialog for AI-powered price suggestions"""
        dialog = tk.Toplevel(self.master)
        dialog.title("AI Price Suggestions")
        dialog.geometry("600x500")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="AI-Powered Pricing", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Product selection
        ttk.Label(dialog, text="Select Product:").pack(pady=5)
        
        products_frame = ttk.Frame(dialog)
        products_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cols = ('PLU', 'Name', 'Current Price', 'Suggested Price', 'Demand')
        tree = ttk.Treeview(products_frame, columns=cols, show='headings')
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(products_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Get pricing suggestions
        suggestions = self.register.get_ai_pricing_suggestions()
        for sugg in suggestions:
            tree.insert('', 'end', values=(sugg['plu'], sugg['name'], f"${sugg['current']:.2f}", 
                                          f"${sugg['suggested']:.2f}", sugg['demand']))
        
        # Apply button
        def apply_suggested():
            selection = tree.selection()
            if selection:
                messagebox.showinfo("Applied", "Suggested price applied!")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Apply Selected", command=apply_suggested).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Refresh", command=lambda: self.show_ai_pricing_dialog() or dialog.destroy()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side='left', padx=5)
    
    def show_multi_store_dialog(self):
        """Dialog for multi-store analytics"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Multi-Store Analytics")
        dialog.geometry("800x600")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Multi-Store Performance Analytics", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Store selector
        store_frame = ttk.Frame(dialog)
        store_frame.pack(pady=5)
        
        ttk.Label(store_frame, text="Select Store:").pack(side='left', padx=5)
        store_var = tk.StringVar(value="All Stores")
        store_combo = ttk.Combobox(store_frame, textvariable=store_var, 
                                     values=['All Stores', 'Store 1', 'Store 2', 'Store 3'], width=20)
        store_combo.pack(side='left', padx=5)
        
        # Date range
        date_frame = ttk.Frame(dialog)
        date_frame.pack(pady=5)
        
        ttk.Label(date_frame, text="Period:").pack(side='left', padx=5)
        period_var = tk.StringVar(value="monthly")
        ttk.Combobox(date_frame, textvariable=period_var, values=['daily', 'weekly', 'monthly', 'yearly'], 
                     width=10).pack(side='left', padx=5)
        
        # Analytics display
        text = scrolledtext.ScrolledText(dialog, width=90, height=30)
        text.pack(padx=10, pady=10, fill='both', expand=True)
        
        def generate_analytics():
            text.delete('1.0', tk.END)
            report = self.register.generate_multi_store_report(store_var.get(), period_var.get())
            text.insert('1.0', report)
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Generate", command=generate_analytics).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export", command=lambda: self._export_analytics(text.get('1.0', tk.END))).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close", command=dialog.destroy).pack(side='left', padx=5)
        
        generate_analytics()
    
    def _export_analytics(self, content):
        """Export multi-store analytics"""
        try:
            with open('multi_store_analytics.txt', 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", "Analytics exported to multi_store_analytics.txt")
        except Exception as e:
            messagebox.showerror("Error", f"Could not export: {e}")
    
    def show_discount_dialog(self):
        """Dialog for applying discount"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Apply Discount")
        dialog.geometry("300x200")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Discount %:").pack(pady=5)
        discount_entry = ttk.Entry(dialog)
        discount_entry.pack(pady=5)
        discount_entry.insert(0, "10")
        
        ttk.Label(dialog, text="Or fixed amount:").pack(pady=5)
        fixed_entry = ttk.Entry(dialog)
        fixed_entry.pack(pady=5)
        
        def apply_discount():
            try:
                pct = float(discount_entry.get()) if discount_entry.get() else 0
                fixed = float(fixed_entry.get()) if fixed_entry.get() else 0
                if pct > 0:
                    self.current_discount_pct = pct
                    self.update_display(f"Discount set: {pct}%")
                elif fixed > 0:
                    self.current_discount_fixed = fixed
                    self.update_display(f"Fixed discount: ${fixed:.2f}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid discount value")
        
        ttk.Button(dialog, text="Apply", command=apply_discount).pack(pady=10)
    
    def show_refund_dialog(self):
        """Dialog for processing refund"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Process Refund")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Transaction ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        txn_entry = ttk.Entry(dialog, width=20)
        txn_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Refund Amount:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Reason:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(dialog, textvariable=reason_var, 
                                    values=["Defective", "Wrong Item", "Customer Request", "Other"],
                                    width=18)
        reason_combo.grid(row=2, column=1, padx=5, pady=5)
        
        def process_refund():
            txn_id = txn_entry.get().strip()
            amount = amount_entry.get().strip()
            reason = reason_var.get()
            if not txn_id or not amount:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            try:
                refund_amt = float(amount)
                # Process refund (would call register.refund())
                self.update_display(f"Refund processed: ${refund_amt:.2f} for TXN {txn_id}")
                messagebox.showinfo("Success", f"Refund of ${refund_amt:.2f} processed")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(dialog, text="Process Refund", command=process_refund).grid(row=3, column=0, columnspan=2, pady=15)
    
    def add_bag_fee(self):
        """Add bag fee to current transaction"""
        bag_fee = 0.10  # Default 10 cents
        # Add as a product
        self.register.add_item('BAG_FEE', 1, bag_fee)
        self.update_display(f"Bag fee: ${bag_fee:.2f}")
    
    def add_crv_fee(self):
        """Add CRV (California Redemption Value) fee"""
        crv_amount = 0.10  # Default
        self.register.add_item('CRV_FEE', 1, crv_amount)
        self.update_display(f"CRV fee: ${crv_amount:.2f}")
    
    def add_atm_fee(self):
        """Add ATM fee to transaction"""
        atm_fee = 2.00  # Default $2
        self.register.add_item('ATM_FEE', 1, atm_fee)
        self.update_display(f"ATM fee: ${atm_fee:.2f}")
    
    def show_item_correction_dialog(self):
        """Dialog for correcting an item in the current transaction"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Item Correction")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Get current transaction items
        items = []
        if self.register.current_transaction:
            items = self.register.current_transaction.items
        
        ttk.Label(dialog, text="Item Number:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(dialog, textvariable=item_var, width=25)
        item_combo['values'] = [f"{i+1}. {it.name} (${it.total:.2f})" for i, it in enumerate(items)]
        item_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="New Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        qty_entry = ttk.Entry(dialog, width=15)
        qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(dialog, text="New Price:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        price_entry = ttk.Entry(dialog, width=15)
        price_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        def apply_correction():
            try:
                idx = item_var.get().split('.')[0]
                if idx:
                    item_idx = int(idx) - 1
                    new_qty = float(qty_entry.get()) if qty_entry.get() else None
                    new_price = float(price_entry.get()) if price_entry.get() else None
                    
                    # Call core correction method
                    success = self.register.correct_item(item_idx, new_qty, new_price)
                    if success:
                        self.update_display(f"Item {item_idx+1} corrected")
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Could not correct item")
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid selection")
        
        ttk.Button(dialog, text="Apply Correction", command=apply_correction).grid(row=3, column=0, columnspan=2, pady=15)
    
    def show_return_dialog(self):
        """Dialog for processing merchandise return"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Return Merchandise")
        dialog.geometry("400x350")
        dialog.transient(self.master)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Original PLU/Barcode:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        plu_entry = ttk.Entry(dialog, width=20)
        plu_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        qty_entry = ttk.Entry(dialog, width=15)
        qty_entry.insert(0, "1")
        qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Reason:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        reason_var = tk.StringVar()
        reason_combo = ttk.Combobox(dialog, textvariable=reason_var, width=18,
                                    values=["Defective", "Wrong Size", "Changed Mind", "Duplicate Order", "Other"])
        reason_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Refund Method:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        refund_var = tk.StringVar(value="Original Payment")
        refund_combo = ttk.Combobox(dialog, textvariable=refund_var, width=18,
                                    values=["Original Payment", "Store Credit", "Cash"])
        refund_combo.grid(row=3, column=1, padx=5, pady=5)
        
        def process_return():
            plu = plu_entry.get().strip()
            qty = float(qty_entry.get() or 1)
            reason = reason_var.get()
            
            if not plu:
                messagebox.showerror("Error", "Please enter product code")
                return
            
            # Add negative quantity to simulate return
            success, msg = self.register.add_item(plu, -qty)
            if success:
                self.update_display(f"Return processed: {plu} x{qty}")
                messagebox.showinfo("Success", f"Return processed for {plu}")
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        ttk.Button(dialog, text="Process Return", command=process_return).grid(row=4, column=0, columnspan=2, pady=15)
    
    def show_scale_dialog(self):
        """Dialog for CAS NTEP scale integration"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Scale / Weight")
        dialog.geometry("300x250")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Scale Status:", font=('Arial', 12)).pack(pady=10)
        status_label = ttk.Label(dialog, text="Connected: No (Simulated)", font=('Arial', 14, 'bold'))
        status_label.pack(pady=10)
        
        ttk.Label(dialog, text="Weight:").pack(pady=5)
        weight_var = tk.StringVar(value="0.000 kg")
        weight_label = ttk.Label(dialog, textvariable=weight_var, font=('Courier', 18, 'bold'))
        weight_label.pack(pady=10)
        
        ttk.Label(dialog, text="Unit Price: $0.00/kg").pack(pady=5)
        
        def simulate_weigh():
            import random
            weight = random.uniform(0.1, 2.0)
            weight_var.set(f"{weight:.3f} kg")
        
        ttk.Button(dialog, text="Simulate Weigh", command=simulate_weigh).pack(pady=15)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_tare_dialog(self):
        """Dialog for tare weight management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Tare Weights")
        dialog.geometry("350x300")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Tare Presets:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Common container weights
        presets = [
            ("None", 0.0),
            ("Small Bag", 0.010),
            ("Medium Bag", 0.025),
            ("Large Bag", 0.050),
            ("Container 1", 0.150),
            ("Container 2", 0.250),
            ("Container 3", 0.500),
        ]
        
        for name, weight in presets:
            btn = ttk.Button(dialog, text=f"{name}: {weight*1000:.0f}g", 
                           command=lambda n=name, w=weight: self.apply_tare(n, w, dialog))
            btn.pack(pady=2, fill='x', padx=20)
        
        ttk.Label(dialog, text="Custom Tare (g):").pack(pady=(15, 5))
        custom_entry = ttk.Entry(dialog, width=10)
        custom_entry.pack()
        
        def apply_custom():
            try:
                grams = float(custom_entry.get())
                self.apply_tare("Custom", grams/1000, dialog)
            except ValueError:
                messagebox.showerror("Error", "Invalid weight")
        
        ttk.Button(dialog, text="Apply Custom", command=apply_custom).pack(pady=5)
    
    def apply_tare(self, name, weight, dialog=None):
        """Apply tare weight to scale"""
        self.current_tare = weight
        self.update_display(f"Tare set: {name} ({weight*1000:.0f}g)")
        if dialog:
            dialog.destroy()

    def generate_z_report(self):
        """Generate and print Z-Report (End of Day)"""
        report = self.register.generate_z_report()

        # Show in dialog
        dialog = tk.Toplevel(self.master)
        dialog.title("Z-Report (End of Day)")
        dialog.geometry("500x600")
        dialog.transient(self.master)

        text = scrolledtext.ScrolledText(dialog, height=30, width=60, font=('Courier', 10))
        text.pack(padx=10, pady=10, fill='both', expand=True)
        text.insert('1.0', report)

        # Save button
        def save_and_close():
            filename = f"zreport_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
            self.save_report(filename, report)
            dialog.destroy()

        ttk.Button(dialog, text="Save & Close", command=save_and_close).pack(pady=10)
        ttk.Button(dialog, text="Print (Simulated)",
                  command=lambda: messagebox.showinfo("Print", "Sending to printer...")).pack(pady=5)
    
    def show_layaway_dialog(self):
        """Dialog for layaway management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Layaway Management")
        dialog.geometry("500x400")
        dialog.transient(self.master)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Create Layaway
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Create Layaway")
        
        if not self.register.current_transaction or self.register.current_transaction.total <= 0:
            ttk.Label(tab1, text="No active transaction to put on layaway.").pack(pady=20)
        else:
            ttk.Label(tab1, text=f"Total Amount: ${self.register.current_transaction.total:.2f}").pack(pady=10)
            
            ttk.Label(tab1, text="Customer ID:").pack(pady=5)
            cust_entry = ttk.Entry(tab1, width=20)
            cust_entry.pack(pady=5)
            
            ttk.Label(tab1, text="Deposit Amount:").pack(pady=5)
            deposit_entry = ttk.Entry(tab1, width=15)
            deposit_entry.insert(0, f"{self.register.current_transaction.total * 0.25:.2f}")
            deposit_entry.pack(pady=5)
            
            ttk.Label(tab1, text="Due Date (YYYY-MM-DD):").pack(pady=5)
            due_entry = ttk.Entry(tab1, width=15)
            due_entry.insert(0, (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d'))
            due_entry.pack(pady=5)
            
            def create_layaway():
                try:
                    deposit = float(deposit_entry.get())
                    due_date = datetime.datetime.strptime(due_entry.get(), '%Y-%m-%d')
                    customer_id = cust_entry.get().strip() or "WALKIN"
                    
                    layaway_id = self.register.create_layaway(deposit, customer_id, due_date)
                    messagebox.showinfo("Success", f"Layaway created: {layaway_id}")
                    dialog.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid input: {e}")
            
            ttk.Button(tab1, text="Create Layaway", command=create_layaway).pack(pady=20)
        
        # Tab 2: Make Payment
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Make Payment")
        
        ttk.Label(tab2, text="Layaway ID:").grid(row=0, column=0, padx=5, pady=5)
        layaway_entry = ttk.Entry(tab2, width=20)
        layaway_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(tab2, text="Payment Amount:").grid(row=1, column=0, padx=5, pady=5)
        payment_entry = ttk.Entry(tab2, width=15)
        payment_entry.grid(row=1, column=1, padx=5, pady=5)
        
        result_label = ttk.Label(tab2, text="", font=('Courier', 12))
        result_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        def make_payment():
            try:
                layaway_id = layaway_entry.get().strip()
                amount = float(payment_entry.get())
                success, new_balance = self.register.process_layaway_payment(layaway_id, amount)
                if success:
                    result_label.config(text=f"Payment accepted. New balance: ${new_balance:.2f}")
                else:
                    messagebox.showerror("Error", "Layaway not found or payment failed")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(tab2, text="Process Payment", command=make_payment).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_gift_card_dialog(self):
        """Dialog for gift card management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Gift Card Management")
        dialog.geometry("400x400")
        dialog.transient(self.master)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Issue Card
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Issue Card")
        
        ttk.Label(tab1, text="Card ID:").grid(row=0, column=0, padx=5, pady=5)
        card_entry = ttk.Entry(tab1, width=20)
        card_entry.grid(row=0, column=1, padx=5, pady=5)
        card_entry.insert(0, f"GC-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        ttk.Label(tab1, text="Initial Amount:").grid(row=1, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(tab1, width=15)
        amount_entry.grid(row=1, column=1, padx=5, pady=5)
        amount_entry.insert(0, "50.00")
        
        def issue_card():
            try:
                card_id = card_entry.get().strip()
                amount = float(amount_entry.get())
                if self.register.issue_gift_card(card_id, amount):
                    messagebox.showinfo("Success", f"Gift card {card_id} issued with ${amount:.2f}")
                    dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(tab1, text="Issue Card", command=issue_card).grid(row=2, column=0, columnspan=2, pady=20)
        
        # Tab 2: Check Balance
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Check Balance")
        
        ttk.Label(tab2, text="Card ID:").grid(row=0, column=0, padx=5, pady=5)
        check_entry = ttk.Entry(tab2, width=20)
        check_entry.grid(row=0, column=1, padx=5, pady=5)
        
        balance_label = ttk.Label(tab2, text="", font=('Courier', 16, 'bold'))
        balance_label.grid(row=1, column=0, columnspan=2, pady=20)
        
        def check_balance():
            card_id = check_entry.get().strip()
            balance = self.register.get_gift_card_balance(card_id)
            balance_label.config(text=f"Balance: ${balance:.2f}")
        
        ttk.Button(tab2, text="Check", command=check_balance).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Tab 3: Redeem
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Redeem")
        
        ttk.Label(tab3, text="Card ID:").grid(row=0, column=0, padx=5, pady=5)
        redeem_card_entry = ttk.Entry(tab3, width=20)
        redeem_card_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(tab3, text="Amount to Redeem:").grid(row=1, column=0, padx=5, pady=5)
        redeem_amount_entry = ttk.Entry(tab3, width=15)
        redeem_amount_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def redeem():
            try:
                card_id = redeem_card_entry.get().strip()
                amount = float(redeem_amount_entry.get())
                if self.register.redeem_gift_card(card_id, amount):
                    messagebox.showinfo("Success", f"Redeemed ${amount:.2f} from card {card_id}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Insufficient balance or invalid card")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(tab3, text="Redeem", command=redeem).grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_customer_dialog(self):
        """Dialog for customer management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Customer Management")
        dialog.geometry("500x500")
        dialog.transient(self.master)
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Add Customer
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Add Customer")
        
        fields = [
            ("Customer ID:", "cust_id", f"CUST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"),
            ("Name:", "name", ""),
            ("Email:", "email", ""),
            ("Phone:", "phone", ""),
        ]
        
        entries = {}
        for i, (label, key, default) in enumerate(fields):
            ttk.Label(tab1, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(tab1, width=25)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, default)
            entries[key] = entry
        
        def add_customer():
            customer_id = entries['cust_id'].get().strip()
            name = entries['name'].get().strip()
            email = entries['email'].get().strip()
            phone = entries['phone'].get().strip()
            
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            
            if self.register.add_customer(customer_id, name, email, phone):
                messagebox.showinfo("Success", f"Customer {name} added")
                dialog.destroy()
        
        ttk.Button(tab1, text="Add Customer", command=add_customer).grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        # Tab 2: Lookup Customer
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Lookup")
        
        ttk.Label(tab2, text="Customer ID:").grid(row=0, column=0, padx=5, pady=5)
        lookup_entry = ttk.Entry(tab2, width=20)
        lookup_entry.grid(row=0, column=1, padx=5, pady=5)
        
        info_text = scrolledtext.ScrolledText(tab2, height=15, width=50)
        info_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        def lookup():
            customer_id = lookup_entry.get().strip()
            customer = self.register.get_customer(customer_id)
            info_text.delete('1.0', tk.END)
            if customer:
                info_text.insert(tk.END, f"Customer ID: {customer['customer_id']}\n")
                info_text.insert(tk.END, f"Name: {customer['name']}\n")
                info_text.insert(tk.END, f"Email: {customer['email']}\n")
                info_text.insert(tk.END, f"Phone: {customer['phone']}\n")
                info_text.insert(tk.END, f"Total Purchases: ${customer['total_purchases']:.2f}\n")
                info_text.insert(tk.END, f"Visit Count: {customer['visit_count']}\n")
            else:
                info_text.insert(tk.END, "Customer not found")
        
        ttk.Button(tab2, text="Lookup", command=lookup).grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_recall_dialog(self):
        """Dialog to recall held transactions"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Recall Held Transaction")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Enter Hold ID:").pack(pady=10)
        entry = ttk.Entry(dialog, width=20)
        entry.pack(pady=5)
        
        def recall():
            hold_id = entry.get().strip()
            if self.register.recall_transaction(hold_id):
                messagebox.showinfo("Success", f"Recalled transaction {hold_id}")
                dialog.destroy()
                self.update_display()
            else:
                messagebox.showerror("Error", "Hold ID not found")
        
        ttk.Button(dialog, text="Recall", command=recall).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)
    
    def show_split_dialog(self):
        """Dialog to split check"""
        if not self.register.current_transaction:
            messagebox.showerror("Error", "No active transaction")
            return
        
        dialog = tk.Toplevel(self.master)
        dialog.title("Split Check")
        dialog.geometry("400x400")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text=f"Total: ${self.register.current_transaction.total:.2f}").pack(pady=10)
        ttk.Label(dialog, text="Number of splits:").pack(pady=5)
        
        spinbox = tk.Spinbox(dialog, from_=2, to=10, width=10)
        spinbox.pack(pady=5)
        
        result_text = scrolledtext.ScrolledText(dialog, height=10, width=40)
        result_text.pack(pady=10, padx=10)
        
        def calculate_splits():
            try:
                num = int(spinbox.get())
                splits = self.register.split_check(num)
                result_text.delete('1.0', tk.END)
                for i, amount in enumerate(splits, 1):
                    result_text.insert(tk.END, f"Check {i}: ${amount:.2f}\n")
            except ValueError:
                messagebox.showerror("Error", "Invalid number")
        
        ttk.Button(dialog, text="Calculate", command=calculate_splits).pack(pady=5)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)

    def show_mode_dialog(self):
        """Dialog to change TEC MA-79 mode"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Select Mode")
        dialog.geometry("400x300")
        dialog.transient(self.master)

        ttk.Label(dialog, text="Current Mode: " + self.register.mode, font=('Courier', 14, 'bold')).pack(pady=10)

        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(pady=20)

        for mode, description in Config.MODES.items():
            btn = tk.Button(mode_frame, text=mode, width=15,
                          bg='#4a4a6a' if mode != self.register.mode else '#2a6a2a',
                          fg='white', font=('Arial', 12),
                          command=lambda m=mode: self.change_mode(m, dialog))
            btn.pack(pady=5)
            ttk.Label(mode_frame, text=description, font=('Arial', 9)).pack()

    def change_mode(self, mode, dialog):
        if self.register.set_mode(mode):
            self.lbl_mode.config(text=f"MODE: {mode}")
            dialog.destroy()
            self.update_display()

    def show_reports_dialog(self):
        """Dialog for comprehensive reporting"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Reports")
        dialog.geometry("600x500")
        dialog.transient(self.master)

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Group Report
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Group/Dept")

        text1 = scrolledtext.ScrolledText(tab1, height=20, width=70)
        text1.pack(padx=10, pady=10, fill='both', expand=True)
        text1.insert('1.0', self.register.generate_group_report())

        ttk.Button(tab1, text="Save to File",
                  command=lambda: self.save_report("group_report.txt", text1.get('1.0', tk.END))).pack(pady=5)

        # Tab 2: PLU Report
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="PLU")

        text2 = scrolledtext.ScrolledText(tab2, height=20, width=70)
        text2.pack(padx=10, pady=10, fill='both', expand=True)
        text2.insert('1.0', self.register.generate_plu_report())

        ttk.Button(tab2, text="Save to File",
                  command=lambda: self.save_report("plu_report.txt", text2.get('1.0', tk.END))).pack(pady=5)

        # Tab 3: Period Report
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Period")

        period_var = tk.StringVar(value='hourly')
        ttk.Radiobutton(tab3, text="Hourly", variable=period_var, value='hourly').pack()
        ttk.Radiobutton(tab3, text="Daily", variable=period_var, value='daily').pack()
        ttk.Radiobutton(tab3, text="Weekly", variable=period_var, value='weekly').pack()
        ttk.Radiobutton(tab3, text="Monthly", variable=period_var, value='monthly').pack()

        text3 = scrolledtext.ScrolledText(tab3, height=15, width=70)
        text3.pack(padx=10, pady=10, fill='both', expand=True)

        def generate_period():
            text3.delete('1.0', tk.END)
            text3.insert('1.0', self.register.generate_period_report(period_var.get()))

        ttk.Button(tab3, text="Generate", command=generate_period).pack(pady=5)
        ttk.Button(tab3, text="Save to File",
                  command=lambda: self.save_report(f"period_{period_var.get()}_report.txt", text3.get('1.0', tk.END))).pack(pady=5)

        # Tab 4: Sales Totals
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Sales Totals")

        text4 = scrolledtext.ScrolledText(tab4, height=20, width=70)
        text4.pack(padx=10, pady=10, fill='both', expand=True)
        text4.insert('1.0', self.register.generate_sales_totals())

        ttk.Button(tab4, text="Refresh",
                  command=lambda: text4.insert('1.0', self.register.generate_sales_totals())).pack(pady=5)
        ttk.Button(tab4, text="Save to File",
                  command=lambda: self.save_report("sales_totals.txt", text4.get('1.0', tk.END))).pack(pady=5)

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def save_report(self, filename, content):
        """Save report to file"""
        try:
            with open(filename, 'w') as f:
                f.write(content)
            messagebox.showinfo("Success", f"Report saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save report: {e}")

    def show_currency_dialog(self):
        """Dialog for currency conversion"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Currency Conversion")
        dialog.geometry("400x300")
        dialog.transient(self.master)
        
        ttk.Label(dialog, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        amount_entry = ttk.Entry(dialog, width=15)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        amount_entry.insert(0, "100.00")
        
        ttk.Label(dialog, text="From:").grid(row=1, column=0, padx=5, pady=5)
        from_var = tk.StringVar(value="USD")
        from_menu = ttk.Combobox(dialog, textvariable=from_var, values=list(Config.EXCHANGE_RATES.keys()), width=10)
        from_menu.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="To:").grid(row=2, column=0, padx=5, pady=5)
        to_var = tk.StringVar(value="EUR")
        to_menu = ttk.Combobox(dialog, textvariable=to_var, values=list(Config.EXCHANGE_RATES.keys()), width=10)
        to_menu.grid(row=2, column=1, padx=5, pady=5)
        
        result_label = ttk.Label(dialog, text="", font=('Courier', 14, 'bold'))
        result_label.grid(row=3, column=0, columnspan=2, pady=20)
        
        def convert():
            try:
                amount = float(amount_entry.get())
                from_curr = from_var.get()
                to_curr = to_var.get()
                result = self.register.convert_currency(amount, from_curr, to_curr)
                symbol = Config.CURRENCY_SYMBOLS.get(to_curr, '$')
                result_label.config(text=f"{symbol}{result:,.2f}" if to_curr != 'BTC' else f"₿{result:.8f}")
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
        
        ttk.Button(dialog, text="Convert", command=convert).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Show current rates
        rates_text = "Current Rates (USD base):\n"
        for curr, rate in list(Config.EXCHANGE_RATES.items())[:5]:
            rates_text += f"  {curr}: {rate}\n"
        ttk.Label(dialog, text=rates_text, justify='left').grid(row=5, column=0, columnspan=2, pady=10)
    
    def show_qr_dialog(self):
        """Dialog for QR code payment"""
        if not QR_AVAILABLE:
            messagebox.showwarning("Not Available", "QR code support requires 'qrcode' and 'PIL' packages")
            return
        
        if not self.register.current_transaction:
            messagebox.showerror("Error", "No active transaction")
            return
        
        dialog = tk.Toplevel(self.master)
        dialog.title("QR Code Payment")
        dialog.geometry("400x500")
        dialog.transient(self.master)
        
        amount = self.register.current_transaction.total
        ttk.Label(dialog, text=f"Amount: ${amount:.2f}").pack(pady=10)
        
        method_var = tk.StringVar(value="BTC")
        ttk.Radiobutton(dialog, text="Bitcoin (BTC)", variable=method_var, value="BTC").pack()
        ttk.Radiobutton(dialog, text="Other", variable=method_var, value="OTHER").pack()
        
        qr_label = ttk.Label(dialog)
        qr_label.pack(pady=20)
        
        def generate():
            img = self.register.generate_payment_qr(amount, method_var.get())
            if img:
                # Convert PIL image for Tkinter
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img)
                qr_label.config(image=photo)
                qr_label.image = photo  # Keep reference
        
        ttk.Button(dialog, text="Generate QR", command=generate).pack(pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)
    
    def show_add_plu_dialog(self):
        """Dialog for adding new PLU/product"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Add New PLU")
        dialog.geometry("400x500")
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Form fields
        fields = [
            ("PLU Code:", "code"),
            ("Product Name:", "name"),
            ("Price:", "price"),
            ("Initial Quantity:", "quantity"),
            ("Department:", "department"),
            ("PLU Code (optional):", "plu"),
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(dialog, width=25)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[key] = entry
        
        # Tax rates checkboxes
        ttk.Label(dialog, text="Tax Rates:").grid(row=len(fields), column=0, padx=5, pady=5, sticky='ne')
        tax_frame = ttk.Frame(dialog)
        tax_frame.grid(row=len(fields), column=1, padx=5, pady=5, sticky='w')
        
        tax_vars = {}
        for i, (tax_name, rate) in enumerate(Config.TAX_RATES.items()):
            var = tk.BooleanVar(value=(tax_name == 'Berkeley'))
            tax_vars[tax_name] = var
            ttk.Checkbutton(tax_frame, text=f"{tax_name} ({rate:.2%})", variable=var).grid(row=i, column=0, sticky='w')
        
        # CRV checkbox
        crv_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="CRV Applicable", variable=crv_var).grid(row=len(fields)+1, column=1, sticky='w', padx=5)
        
        # Open price checkbox
        open_price_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dialog, text="Allow Price Override", variable=open_price_var).grid(row=len(fields)+2, column=1, sticky='w', padx=5)
        
        def save_plu():
            try:
                code = entries['code'].get().strip()
                name = entries['name'].get().strip()
                price = float(entries['price'].get())
                quantity = int(entries['quantity'].get())
                department = entries['department'].get().strip() or "General"
                plu_code = entries['plu'].get().strip() or None
                
                selected_taxes = [tax for tax, var in tax_vars.items() if var.get()]
                
                product = Product(
                    code=code,
                    name=name,
                    price=price,
                    quantity=quantity,
                    department=department,
                    tax_rates=selected_taxes,
                    track_inventory=True,
                    open_price=open_price_var.get(),
                    plu_code=plu_code,
                    crv_applicable=crv_var.get(),
                    crv_rate=0.05 if crv_var.get() else 0.0
                )
                
                self.register.add_product(product)
                messagebox.showinfo("Success", f"Added PLU: {name}")
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
        
        ttk.Button(dialog, text="Save PLU", command=save_plu).grid(row=len(fields)+3, column=0, columnspan=2, pady=20)
    
    def show_department_dialog(self):
        """Dialog for department management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Department Management")
        dialog.geometry("600x500")
        dialog.transient(self.master)
        
        # Get unique departments
        departments = {}
        for product in self.register.products.values():
            dept = product.department
            if dept not in departments:
                departments[dept] = {'products': [], 'total_value': 0}
            departments[dept]['products'].append(product)
            departments[dept]['total_value'] += product.price * product.quantity
        
        # Treeview for departments
        tree = ttk.Treeview(dialog, columns=('Products', 'Total Value'), show='tree headings')
        tree.heading('#0', text='Department')
        tree.heading('Products', text='Products')
        tree.heading('Total Value', text='Inventory Value')
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        for dept_name, data in sorted(departments.items()):
            item_count = len(data['products'])
            value = data['total_value']
            tree.insert('', 'end', text=dept_name, values=(item_count, f"${value:.2f}"))
        
        # Assign product to department section
        ttk.Label(dialog, text="Reassign Product to Department:").pack(pady=(10, 5))
        
        assign_frame = ttk.Frame(dialog)
        assign_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(assign_frame, text="Product Code:").grid(row=0, column=0, padx=5)
        product_entry = ttk.Entry(assign_frame, width=15)
        product_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(assign_frame, text="New Department:").grid(row=0, column=2, padx=5)
        dept_entry = ttk.Entry(assign_frame, width=20)
        dept_entry.grid(row=0, column=3, padx=5)
        
        def assign_department():
            code = product_entry.get().strip()
            new_dept = dept_entry.get().strip()
            
            if code in self.register.products:
                product = self.register.products[code]
                product.department = new_dept
                self.register.add_product(product)
                messagebox.showinfo("Success", f"Assigned {product.name} to {new_dept}")
                dialog.destroy()
                self.show_department_dialog()  # Refresh
            else:
                messagebox.showerror("Error", "Product not found")
        
        ttk.Button(assign_frame, text="Assign", command=assign_department).grid(row=0, column=4, padx=5)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_inventory_dialog(self):
        """Dialog for inventory management"""
        dialog = tk.Toplevel(self.master)
        dialog.title("Inventory Management")
        dialog.geometry("800x600")
        dialog.transient(self.master)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: All Products
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="All Products")
        
        # Treeview for products
        columns = ('Code', 'Name', 'Price', 'Stock', 'Department', 'Status')
        tree = ttk.Treeview(tab1, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tab1, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Populate tree
        for code, product in sorted(self.register.products.items()):
            status = "LOW" if product.quantity < 10 else "OK" if product.quantity > 0 else "OUT"
            tree.insert('', 'end', values=(
                code, product.name, f"${product.price:.2f}",
                product.quantity, product.department, status
            ))
        
        # Tab 2: Low Stock
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Low Stock Alerts")
        
        low_stock_tree = ttk.Treeview(tab2, columns=columns[:5], show='headings')
        for col in columns[:5]:
            low_stock_tree.heading(col, text=col)
            low_stock_tree.column(col, width=120)
        low_stock_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        for code, product in sorted(self.register.products.items()):
            if product.quantity < 10:
                low_stock_tree.insert('', 'end', values=(
                    code, product.name, f"${product.price:.2f}",
                    product.quantity, product.department
                ))
        
        # Tab 3: Stock Adjustment
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Adjust Stock")
        
        ttk.Label(tab3, text="Product Code:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        code_entry = ttk.Entry(tab3, width=20)
        code_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(tab3, text="Adjustment (+/-):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        adj_entry = ttk.Entry(tab3, width=20)
        adj_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(tab3, text="Reason:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        reason_entry = ttk.Entry(tab3, width=30)
        reason_entry.grid(row=2, column=1, padx=5, pady=5)
        reason_entry.insert(0, "Stock adjustment")
        
        def adjust_stock():
            try:
                code = code_entry.get().strip()
                adjustment = int(adj_entry.get())
                reason = reason_entry.get().strip()
                
                if code in self.register.products:
                    product = self.register.products[code]
                    new_qty = product.quantity + adjustment
                    if new_qty < 0:
                        messagebox.showerror("Error", "Cannot reduce stock below 0")
                        return
                    
                    product.quantity = new_qty
                    self.register.add_product(product)
                    
                    # Log adjustment
                    conn = self.register.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO inventory_log (product_code, adjustment, reason, new_quantity, timestamp, clerk_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (code, adjustment, reason, new_qty, datetime.datetime.now().isoformat(),
                          self.register.current_clerk['id'] if self.register.current_clerk else 'system'))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Success", f"Stock adjusted. New quantity: {new_qty}")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Product not found")
            except ValueError:
                messagebox.showerror("Error", "Invalid adjustment amount")
        
        ttk.Button(tab3, text="Adjust Stock", command=adjust_stock).grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def handle_payment(self, method):
        if not self.register.current_transaction:
            return
        
        remaining = self.register.current_transaction.total - sum(
            p['amount'] for p in self.register.current_transaction.payments
        )
        
        if remaining <= 0:
            return
        
        if method == "Cash":
            dialog = tk.Toplevel(self.master)
            dialog.title("Cash Payment")
            dialog.transient(self.master)
            
            ttk.Label(dialog, text=f"Total: {Config.CURRENCY_SYMBOL}{remaining:.2f}").pack(pady=5)
            ttk.Label(dialog, text="Amount Tendered:").pack(pady=5)
            entry_amount = ttk.Entry(dialog)
            entry_amount.pack(pady=5)
            entry_amount.insert(0, f"{remaining:.2f}")
            
            def process():
                try:
                    amount = float(entry_amount.get())
                    success, rem = self.register.add_payment(method, amount)
                    if success and rem <= 0:
                        messagebox.showinfo("Complete", f"Change: {Config.CURRENCY_SYMBOL}{self.register.current_transaction.change:.2f}")
                        self.register.current_transaction = None
                        self.register.start_transaction()
                    dialog.destroy()
                    self.update_display()
                except ValueError:
                    messagebox.showerror("Error", "Invalid amount")
            
            ttk.Button(dialog, text="Process", command=process).pack(pady=10)
            entry_amount.bind('<Return>', lambda e: process())
            entry_amount.focus()
        else:
            success, rem = self.register.add_payment(method, remaining)
            if success and rem <= 0:
                messagebox.showinfo("Complete", "Transaction complete!")
                self.register.current_transaction = None
                self.register.start_transaction()
            self.update_display()
    
    def update_display(self):
        text = f"{Config.STORE_NAME}\n"
        text += f"Mode: {self.register.mode} | Clerk: {self.register.current_clerk['name'] if self.register.current_clerk else 'None'}\n"
        text += "=" * 50 + "\n\n"
        
        if self.register.current_transaction:
            for i, item in enumerate(self.register.current_transaction.items, 1):
                if not item.voided:
                    text += f"{i:2d}. {item.name[:20]:20s} x{item.quantity:4.1f} {Config.CURRENCY_SYMBOL}{item.total:8.2f}\n"
            
            text += "\n" + "=" * 50 + "\n"
            text += f"Subtotal: {Config.CURRENCY_SYMBOL}{self.register.current_transaction.subtotal:10.2f}\n"
            text += f"Tax:      {Config.CURRENCY_SYMBOL}{self.register.current_transaction.tax_total:10.2f}\n"
            if self.register.current_transaction.crv_total > 0:
                text += f"CRV:      {Config.CURRENCY_SYMBOL}{self.register.current_transaction.crv_total:10.2f}\n"
            text += f"TOTAL:    {Config.CURRENCY_SYMBOL}{self.register.current_transaction.total:10.2f}\n"
            
            total_paid = sum(p['amount'] for p in self.register.current_transaction.payments)
            if total_paid > 0:
                text += f"Paid:     {Config.CURRENCY_SYMBOL}{total_paid:10.2f}\n"
                remaining = self.register.current_transaction.total - total_paid
                if remaining > 0:
                    text += f"Due:      {Config.CURRENCY_SYMBOL}{remaining:10.2f}\n"
        else:
            text += "No active transaction\n"
        
        if self.input_buffer:
            text += f"\nInput: {self.input_buffer}"
        
        self.txt_display.delete('1.0', tk.END)
        self.txt_display.insert('1.0', text)
        self.txt_display.see(tk.END)


# ==================== MAIN ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = ReggieStarrGUI(root)
    root.mainloop()
