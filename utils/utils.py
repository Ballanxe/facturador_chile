from facturas.models import Factura
from guia_despacho.models import guiaDespacho
from nota_credito.models import notaCredito
from nota_debito.models import notaDebito


def validarModelPorDoc(tipo_doc):
    """
    Funcion para validar y asignar un modelo a el documento

    @author Rodrigo Boet (rudmanmrrod@gmail.com)
    @date 09-04-2019
    @param tipo_doc variable que define el tipo de documento
    @return objeto con del modelo asignado para el documento
    """
    if tipo_doc == 'FACT_ELEC':
        modelo = Factura
    elif tipo_doc == 'GUIA_DES_ELEC':
        modelo = guiaDespacho
    elif tipo_doc == 'NOTA_DEB_ELEC':
        modelo = notaDebito
    elif tipo_doc == 'NOTA_CRE_ELEC':
        modelo = notaCredito
    return modelo
