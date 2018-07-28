import os
from django import VERSION
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.template import defaultfilters

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import lightgrey
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Equipment, EquipmentBorrowing

COLUMN_1 = 1.5 * cm
COLUMN_2 = 6 * cm
COLUMN_3 = 11.5 * cm
COLUMN_4 = 15 * cm


class ExportMaterial:

    def __init__(self):
        self.filename = 'materiel-vertigo-{}.pdf'.format(defaultfilters.date(timezone.now(), 'Y-m-j'))
        self.response = HttpResponse(content_type='application/pdf')
        self.response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)
        self.page = canvas.Canvas(self.response, pagesize=A4)
        self.page.setLineCap(1)

    def _entete_de_liste(self, equipment, bottom):
        self.page.setFont('EffraMedium', 10)
        self.page.drawString(COLUMN_1, bottom * cm, equipment.plural.upper())
        self.page.drawString(COLUMN_2, bottom * cm, 'RESPONSABLE')
        self.page.drawString(COLUMN_3, bottom * cm, 'DEPUIS LE')
        self.page.drawString(COLUMN_4, bottom * cm, 'EMPRUNTÉ{} PAR'.format('E' if equipment.gender == 'la' else ''))

    def _pied_de_page(self):
        logo = os.path.join(settings.BASE_DIR, 'static/img/logo.jpg')
        self.page.drawImage(logo, 16.5 * cm, 0.8 * cm, width=100, height=50)  # 16.5  0.8
        self.page.setFont('King', 10)
        self.page.drawString(1.5 * cm, 2 * cm, 'Association Vertigo - escalade, canyoning, randonnée')
        self.page.setLineWidth(0.5)
        self.page.line(1.5 * cm, 1.8 * cm, 16 * cm, 1.8 * cm)  # 14.8
        self.page.setFont('King', 8)
        self.page.drawString(1.5 * cm, 1.4 * cm, 'Liste d\'emprunt du matériel.')
        self.page.drawString(1.5 * cm, 1.0 * cm, 'Tout usage en dehors du cadre de l\'association est interdit.')

    def _draw_line(self, y, color, width):
        self.page.setLineWidth(width)
        self.page.setStrokeColor(color)
        self.page.line(COLUMN_1, y * cm, 19.5 * cm, y * cm)

    def pdf_material(self):

        self.page.setTitle('Liste du matériel')
        self.page.setSubject('Liste du matériel à imprimer pour le jeudi soir')
        self.page.setAuthor('Association Vertigo')
        self.page.setCreator('Django {}.{}.{}'.format(VERSION[0], VERSION[1], VERSION[2]))

        # Fonts
        pdfmetrics.registerFont(
            TTFont('EffraLight', os.path.join(settings.BASE_DIR, 'static/fonts/effra_std_lt-webfont.ttf')))
        pdfmetrics.registerFont(
            TTFont('EffraMedium', os.path.join(settings.BASE_DIR, 'static/fonts/effra_std_md-webfont.ttf')))
        pdfmetrics.registerFont(
            TTFont('King', os.path.join(settings.BASE_DIR, 'static/fonts/KIN668.ttf')))

        # Page header
        self.page.setFont('EffraMedium', 20)
        self.page.drawString(COLUMN_1, 28 * cm, 'LISTE DU MATERIEL')
        self.page.setFont('EffraLight', 10)
        self.page.drawString(COLUMN_1, 27.6 * cm, 'Export du {}'.format(
            defaultfilters.date(timezone.now(), 'l j F Y')))  # ' @ H:m'

        # Set footer
        self._pied_de_page()

        y = 26

        # Loop over equipment types
        for equipment in Equipment.TYPE_LIST:

            borrowing_list = EquipmentBorrowing.objects.filter(item__type=equipment.url)\
                .order_by('item__ref', '-date', '-id').distinct('item__ref').exclude(item__status=False)

            self._entete_de_liste(equipment, y)
            self.page.setFont('EffraLight', 10)

            y += -0.5

            for borrow in borrowing_list:
                self._draw_line(y + 0.35, lightgrey, .5)
                message = " ({})".format(borrow.item.caution) if borrow.item.caution else ''
                self.page.drawString(COLUMN_1, y*cm, "{} n°{}{}".format(equipment.singular, borrow.item.ref, message))
                self.page.drawString(COLUMN_2, y*cm, borrow.user.get_full_name())
                self.page.drawString(COLUMN_3, y*cm, defaultfilters.date(borrow.date, 'j F'))

                y += -0.5
                if y < 5:
                    self.page.showPage()
                    self._entete_de_liste(equipment, 28)
                    self._pied_de_page()
                    self.page.setFont('EffraLight', 10)
                    y = 27.5

            y += -0.5

        # Save page
        self.page.showPage()
        self.page.save()

        return self.response
