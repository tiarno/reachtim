Title: How To Create Keywords Metadata From Index Terms
Category: XML
Date: 2014-Sep-30
Status: Draft
Tags: how-to, web
Summary: How to keyword metadata from index terms with DocBook

<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template name="keywordset">
    <xsl:variable name="section_level">
      <xsl:number value="count(ancestor-or-self::d:section)" />
    </xsl:variable>
    <!-- if we are not on a part or book, and we have indexterms -->
    <xsl:if test="not(self::part) and  not(self::book) and .//d:indexterm">
      <xsl:variable name="indexterms">
        <xsl:choose>
          <xsl:when test="$section_level = 0" />
          <xsl:when test="$section_level &lt; $chunk.section.depth">
            <!--  If we're not at the bottom of the tree, get all index terms that are direct children and all index terms
                  that are children of non-section elements.
                  Note: index terms that are children of subsections will be handled recursively.
            -->
            <xsl:copy-of select="./d:indexterm/d:primary|./*[not(self::d:section)]//d:indexterm/d:primary" />
          </xsl:when>

          <xsl:otherwise>
            <!-- Otherwise, get all indexterm children -->
            <xsl:copy-of select=".//d:indexterm/d:primary" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>
      <xsl:variable name="indexterms-unique">
        <xsl:for-each select="exsl:node-set($indexterms)/*[not(. = preceding-sibling::*)]">
          <xsl:value-of select="normalize-space(.)" />
          <xsl:if test="not(position() =  last())">,</xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <meta name="keywords">
      <xsl:attribute name="content">
        <xsl:value-of select="$indexterms-unique" />
      </xsl:attribute>
    </meta>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>

<!-- see this: http://users.atw.hu/xsltcookbook2/xsltckbk2-chp-5-sect-1.html -->