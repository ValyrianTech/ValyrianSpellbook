#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from taghash.taghash import TagHash


class TestTagHash(object):

    def test_given_no_input_value_when_initializing_a_taghash_then_a_taghash_object_is_returned(self):
        assert isinstance(TagHash(), TagHash)

    def test_given_a_string_as_input_value_when_initializing_a_taghash_then_a_taghash_object_is_returned(self):
        assert isinstance(TagHash('some normal string'), TagHash)

    def test_given_a_unicode_string_as_input_value_when_initializing_a_taghash_then_a_taghash_object_is_returned(self):
        assert isinstance(TagHash(u'some unicode string'), TagHash)

    @pytest.mark.parametrize('tags', [
        (),
        [],
        None,
        42,
        ['a', 'list'],
        True,
        False,
    ])
    def test_given_anything_that_is_not_a_string_as_input_value_when_initializing_a_taghash_then_exception_is_raised(self, tags):
        print(tags, type(tags))

        with pytest.raises(Exception):
            TagHash(tags=tags)

    @pytest.mark.parametrize('tags', [
        'this is a test message',
        'This is a test message',
        'this Is a test message',
        'this is A test message',
        'this is a test message test',
        'a test message is this',
        'this is à test message',
        'this is a test méssage',
        'this is a test #message',
        'this       is a test message',
        'this is a - test  message',
        'this is_ a test message',
        'this is_ a test message&(§!)$[]:;,=',
    ])
    def test_given_tags_that_should_result_in_the_same_taghash_when_initializing_a_taghash_then_a_taghash_is_correct(self, tags):
        control_taghash = TagHash(tags='this is a test message').get()
        assert TagHash(tags=tags).get() == control_taghash

    @pytest.mark.parametrize('letter, variations', [
        (u'A', u'ÁáÀàÂâǍǎĂăÃãẢảȦȧẠạÄäÅåḀḁĀāĄąᶏȺⱥȀȁẤấẦầẪẫẨẩẬậẮắẰằẴẵẲẳẶặǺǻǠǡǞǟȀȁȂȃⱭɑᴀⱯɐɒＡａ'),
        (u'B', u'ḂḃḄḅḆḇɃƀƁɓƂƃᵬᶀʙＢｂ'),
        (u'C', u'ĆćĈĉČčĊċÇçḈḉȻȼƇƈɕᴄＣｃ'),
        (u'D', u'ĎďḊḋḐḑḌḍḒḓḎḏĐđÐðD̦dƉɖƊɗƋƌᵭᶁᶑȡᴅＤｄÞþǱǲǳǄǅǆ'),
        (u'E', u'ÉéÈèÊêḘḙĚěĔĕẼẽḚḛẺẻĖėËëĒēȨȩĘęᶒɆɇȄȅẾếỀềỄễỂểḜḝḖḗḔḕȆȇẸẹỆệⱸᴇＥｅ'),
        (u'F', u'ḞḟƑƒᵮᶂꜰＦｆ'),
        (u'G', u'ǴǵĞğĜĝǦǧĠġĢģḠḡǤǥƓɠᶃɢＧｇ'),
        (u'H', u'ĤĥȞȟḦḧḢḣḨḩḤḥḪḫH̱ẖĦħⱧⱨɦʰʜＨｈ'),
        (u'I', u'ÍíÌìĬĭÎîǏǐÏïḮḯĨĩĮįĪīỈỉȈȉȊȋỊịḬḭƗɨᵻᶖİiIıɪＩｉﬁ'),
        (u'J', u'ĴĵɈɉǰȷʝɟʄᴊＪｊ'),
        (u'K', u'ḰḱǨǩĶķḲḳḴḵƘƙⱩⱪᶄᶄꝀꝁᴋＫｋ'),
        (u'L', u'ĹĺĽľĻļḶḷḸḹḼḽḺḻŁłĿŀȽƚⱠⱡⱢɫɬᶅɭȴʟ'),
        (u'M', u'ḾḿṀṁṂṃᵯᶆⱮɱᴍＭｍ'),
        (u'N', u'ŃńǸǹŇňÑñṄṅŅņṆṇṊṋṈṉƝɲȠƞᵰᶇɳȵɴＮｎǊǋǌ'),
        (u'O', u'ÓóÒòŎŏÔôỐốỒồỖỗỔổǑǒÖöȪȫŐőÕõṌṍṎṏȬȭȮȯȰȱØøǾǿǪǫǬǭŌōṒṓṐṑỎỏȌȍȎȏƠơỚớỜờỠỡỞởỢợỌọỘộƟɵⱺᴏＯｏŒœᴔ'),
        (u'P', u'ṔṕṖṗⱣᵽƤƥP̃p̃ᵱᶈᴘＰｐ'),
        (u'Q', u'ɊɋʠＱｑ'),
        (u'R', u'ŔŕŘřṘṙŖŗȐȑȒȓṚṛṜṝṞṟɌɍⱤɽᵲᶉɼɾᵳʀＲｒ'),
        (u'S', u'ſßŚśṤṥŜŝŠšṦṧṠṡẛŞşṢṣṨṩȘșS̩s̩ᵴᶊʂȿꜱＳｓ'),
        (u'T', u'ŤťṪṫŢţṬṭȚțṰṱṮṯŦŧȾⱦƬƭƮʈT̈ẗᵵƫȶᴛＴｔ'),
        (u'U', u'ÚúÙùŬŭÛûǓǔŮůÜüǗǘǛǜǙǚǕǖŰűŨũṸṹŲųŪūṺṻỦủȔȕȖȗƯưỨứỪừỮữỬửỰựỤụṲṳṶṷṴṵɄʉᵾᶙᴜＵｕꜶꜷȢȣᵫ'),
        (u'V', u'ṼṽṾṿƲʋᶌᶌⱱⱴᴠＶｖ'),
        (u'W', u'ẂẃẀẁŴŵẄẅẆẇẈẉẘẘⱲⱳᴡＷｗ'),
        (u'X', u'ẌẍẊẋᶍＸｘ'),
        (u'Y', u'ÝýỲỳŶŷẙŸÿỸỹẎẏȲȳỶỷỴỵɎɏƳƴʏＹｙ'),
        (u'Z', u'ŹźẐẑŽžŻżẒẓẔẕƵƶȤȥⱫⱬᵶᶎʐʑɀᴢＺｚ'),
    ])
    def test_given_a_variation_of_a_letter_when_normalizing_a_tag_then_it_is_replaced_with_its_base_letter(self, letter, variations):
        taghash = TagHash()

        for variation in variations:
            print(variation)
            assert taghash.normalize_tag(variation) == letter
