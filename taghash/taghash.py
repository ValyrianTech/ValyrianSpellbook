#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib


class TagHash(object):
    def __init__(self, tags=""):
        """
        Constructor of TagHash

        A TagHash is a sha256 hash of one or more tags that still returns the same value under certain conditions like when
        the order of the tags is changed, a tag occurs multiple times, tags are case-insensitive and even when variations of a
        letter are used instead of its base letter (e.g. à vs a)

        :param tags: A string or unicode containing one or multiple tags (optional)
        """
        self.taghash = ''

        # If tags are given as input it must be a string
        if isinstance(tags, str):
            # Convert all tags to unicode
            self.tags = [tag for tag in tags.split()]
            self.calculate()
        else:
            raise Exception('Expected a string or unicode as input value but got %s instead: %s' % (type(tags), tags))

    def calculate(self):
        """
        Calculate the sha256 hash of the sorted unique normalized tags

        :return: A hash string
        """
        concatenated = ''
        # Sort each unique normalized tag and concatenate them
        for normalized_tag in sorted(set(self.normalize_tag(tag) for tag in self.tags)):
            concatenated += normalized_tag

        self.taghash = hashlib.sha256(concatenated.encode()).hexdigest()
        return self.taghash

    @staticmethod
    def normalize_tag(tag):
        """
        This helper function will normalize a single tag, the normalization process consists of these steps:
        1. strip the tag of newline characters and spaces
        2. replace characters with accents to the respective character without accent
        3. remove characters that are not alphanumerical (a-Z, 0-9)
        4. change all characters to upper case

        :param tag: A string (unicode) that contains a single tag (no spaces)
        :return: A normalized tag
        """
        # Strip newline characters, tabs and extra spaces
        normalized_tag = tag.strip()

        # Replace variations of letters with their base letter
        normalized_tag = normalized_tag.translate({ord(c): u'A' for c in u'ÁáÀàÂâǍǎĂăÃãẢảȦȧẠạÄäÅåḀḁĀāĄąᶏȺⱥȀȁẤấẦầẪẫẨẩẬậẮắẰằẴẵẲẳẶặǺǻǠǡǞǟȀȁȂȃⱭɑᴀⱯɐɒＡａ'})
        normalized_tag = normalized_tag.translate({ord(c): u'B' for c in u'ḂḃḄḅḆḇɃƀƁɓƂƃᵬᶀʙＢｂ'})
        normalized_tag = normalized_tag.translate({ord(c): u'C' for c in u'ĆćĈĉČčĊċÇçḈḉȻȼƇƈɕᴄＣｃ'})
        normalized_tag = normalized_tag.translate({ord(c): u'D' for c in u'ĎďḊḋḐḑḌḍḒḓḎḏĐđÐðD̦dƉɖƊɗƋƌᵭᶁᶑȡᴅＤｄÞþǱǲǳǄǅǆ'})
        normalized_tag = normalized_tag.translate({ord(c): u'E' for c in u'ÉéÈèÊêḘḙĚěĔĕẼẽḚḛẺẻĖėËëĒēȨȩĘęᶒɆɇȄȅẾếỀềỄễỂểḜḝḖḗḔḕȆȇẸẹỆệⱸᴇＥｅ'})
        normalized_tag = normalized_tag.translate({ord(c): u'F' for c in u'ḞḟƑƒᵮᶂꜰＦｆ'})
        normalized_tag = normalized_tag.translate({ord(c): u'G' for c in u'ǴǵĞğĜĝǦǧĠġĢģḠḡǤǥƓɠᶃɢＧｇ'})
        normalized_tag = normalized_tag.translate({ord(c): u'H' for c in u'ĤĥȞȟḦḧḢḣḨḩḤḥḪḫH̱ẖĦħⱧⱨɦʰʜＨｈ'})
        normalized_tag = normalized_tag.translate({ord(c): u'I' for c in u'ÍíÌìĬĭÎîǏǐÏïḮḯĨĩĮįĪīỈỉȈȉȊȋỊịḬḭƗɨᵻᶖİiIıɪＩｉﬁ'})
        normalized_tag = normalized_tag.translate({ord(c): u'J' for c in u'ĴĵɈɉǰȷʝɟʄᴊＪｊ'})
        normalized_tag = normalized_tag.translate({ord(c): u'K' for c in u'ḰḱǨǩĶķḲḳḴḵƘƙⱩⱪᶄᶄꝀꝁᴋＫｋ'})
        normalized_tag = normalized_tag.translate({ord(c): u'L' for c in u'ĹĺĽľĻļḶḷḸḹḼḽḺḻŁłĿŀȽƚⱠⱡⱢɫɬᶅɭȴʟ'})
        normalized_tag = normalized_tag.translate({ord(c): u'M' for c in u'ḾḿṀṁṂṃᵯᶆⱮɱᴍＭｍ'})
        normalized_tag = normalized_tag.translate({ord(c): u'N' for c in u'ŃńǸǹŇňÑñṄṅŅņṆṇṊṋṈṉƝɲȠƞᵰᶇɳȵɴＮｎǊǋǌ'})
        normalized_tag = normalized_tag.translate({ord(c): u'O' for c in u'ÓóÒòŎŏÔôỐốỒồỖỗỔổǑǒÖöȪȫŐőÕõṌṍṎṏȬȭȮȯȰȱØøǾǿǪǫǬǭŌōṒṓṐṑỎỏȌȍȎȏƠơỚớỜờỠỡỞởỢợỌọỘộƟɵⱺᴏＯｏŒœᴔ'})
        normalized_tag = normalized_tag.translate({ord(c): u'P' for c in u'ṔṕṖṗⱣᵽƤƥP̃p̃ᵱᶈᴘＰｐ'})
        normalized_tag = normalized_tag.translate({ord(c): u'Q' for c in u'ɊɋʠＱｑ'})
        normalized_tag = normalized_tag.translate({ord(c): u'R' for c in u'ŔŕŘřṘṙŖŗȐȑȒȓṚṛṜṝṞṟɌɍⱤɽᵲᶉɼɾᵳʀＲｒ'})
        normalized_tag = normalized_tag.translate({ord(c): u'S' for c in u'ſßŚśṤṥŜŝŠšṦṧṠṡẛŞşṢṣṨṩȘșS̩s̩ᵴᶊʂȿꜱＳｓ'})
        normalized_tag = normalized_tag.translate({ord(c): u'T' for c in u'ŤťṪṫŢţṬṭȚțṰṱṮṯŦŧȾⱦƬƭƮʈT̈ẗᵵƫȶᴛＴｔ'})
        normalized_tag = normalized_tag.translate({ord(c): u'U' for c in u'ÚúÙùŬŭÛûǓǔŮůÜüǗǘǛǜǙǚǕǖŰűŨũṸṹŲųŪūṺṻỦủȔȕȖȗƯưỨứỪừỮữỬửỰựỤụṲṳṶṷṴṵɄʉᵾᶙᴜＵｕꜶꜷȢȣᵫ'})
        normalized_tag = normalized_tag.translate({ord(c): u'V' for c in u'ṼṽṾṿƲʋᶌᶌⱱⱴᴠＶｖ'})
        normalized_tag = normalized_tag.translate({ord(c): u'W' for c in u'ẂẃẀẁŴŵẄẅẆẇẈẉẘẘⱲⱳᴡＷｗ'})
        normalized_tag = normalized_tag.translate({ord(c): u'X' for c in u'ẌẍẊẋᶍＸｘ'})
        normalized_tag = normalized_tag.translate({ord(c): u'Y' for c in u'ÝýỲỳŶŷẙŸÿỸỹẎẏȲȳỶỷỴỵɎɏƳƴʏＹｙ'})
        normalized_tag = normalized_tag.translate({ord(c): u'Z' for c in u'ŹźẐẑŽžŻżẒẓẔẕƵƶȤȥⱫⱬᵶᶎʐʑɀᴢＺｚ'})

        # Remove any non-alphanumerical characters
        normalized_tag = ''.join(c for c in normalized_tag if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

        # Return the tag in upper case
        return normalized_tag.upper()

    def add_tag(self, tag):
        """
        Add a tag to the TagHash object and re-calculate

        :param tag: A string or unicode that contains a single tag
        """
        if isinstance(tag, str):
            # Convert to unicode before adding the tag
            self.tags.append(tag.decode('utf-8'))
            self.calculate()

    def remove_tag(self, tag):
        """
        Remove a single tag from the TagHash object

        :param tag: A string or unicode that contains the tag to be removed
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.calculate()

    def clear(self):
        """
        Clear all tags in the TagHash object
        """
        self.tags = []
        self.calculate()

    def get(self):
        """
        Get the taghash

        :return: A taghash
        """
        return self.taghash
