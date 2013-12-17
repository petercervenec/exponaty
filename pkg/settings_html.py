# coding=utf-8

class SettingsHtml:
    def __init__(self):
        pass

    def html_header(self, exhibit, **additional):
        max_score=exhibit.get_max_score()
        if max_score is None:
            max_score='žiadne'
        else:
            max_score=str(max_score)
        user_name=exhibit.get_user_name()
        if not user_name:
            user_name='nikto'
        user_name=strip_html(user_name)
        return u"""

       <div class="header">
            <div>
                <div class="max_score">
                    <div class="max_score_key"> najlepšie denné skóre: </div>
                    <div class="max_score_value"> {max_score} </div>
                </div>
                <div class="user_name">
                    <div class="user_name_key"> prihlásený: </div>
                    <div class="user_name_value"> {user_name} </div>
                </div>
            </div>
        </div>
        """.format(user_name=user_name, max_score=max_score)


    def html_footer(self, exhibit, **additional):
        return u"""
        <div class="footer">
        </div>
        """.format()


    def html_welcome(self, exhibit, **additional):
        return u"""
        {header}
        <div class="greeting">
            <div class="greeting_key"> Vitaj </div>
            <div class="greeting_value"> {user_name} </div>
            <div class="greeting_excl"> ! </div>
        </div>
        {footer}
        """.format(header=self.html_header(exhibit),
                   footer=self.html_footer(exhibit),
                   user_name=exhibit.get_user_name())


    def html_bye(self, exhibit, **additional):
        return u"""
        {header}
        <h1> Odhlásený: {user_name} </h1>
        {footer}
        """.format(header=self.html_header(exhibit),
                   footer=self.html_footer(exhibit),
                   user_name=exhibit.get_user_name())


    def html_instr(self, exhibit, **additional):
        return u"""
        {header}
        <div class='instr'>
            {instr}
        </div>
        {footer}
        """.format(header=self.html_header(exhibit),
                   footer=self.html_footer(exhibit),
                   instr=self.instr)


    def html_info(self, exhibit, **additional):
        info_template = """
        <div class="line">
        <div class="key"> {key} </div>
        <div class="sep"> : </div>
        <div class="value"> {value} </div>
        </div>
        """
        info = '\n'.join(info_template.format(key=key,
                                              value=phormat%getter(exhibit, additional))
                         for key, (getter, phormat) in self.info.items())
        return u"""
        {header}
        <div class='info'>
            {info}
        </div>
        {footer}
        """.format(header=self.html_header(exhibit),
                   footer=self.html_footer(exhibit),
                   info=info)


    def html_score(self, exhibit, **additional):
        return u"""
        {header}
        <div class='score'>
            <div class="score_key"> {score_line_1} </div>
            <div class="score_value"> {score} </div>
            <div class="score_key"> {score_line_2} </div>
        </div>
        {footer}
        """.format(header=self.html_header(exhibit),
                   footer=self.html_footer(exhibit),
                   score_line_1=self.score_line_1,
                   score_line_2=self.score_line_2,
                   score=self.max_score_format % (exhibit.score,))

import re

def strip_html(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
