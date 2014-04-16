<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
    xmlns:t="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs xd"
    version="2.0">
    <xsl:output method="xhtml"/>
    <xd:doc scope="stylesheet">
        <xd:desc>
            <xd:p><xd:b>Created on:</xd:b> Apr 11, 2014</xd:p>
            <xd:p><xd:b>Author:</xd:b> elli</xd:p>
            <xd:p></xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:strip-space elements="*"/>
    <xsl:template match="/t:listBibl">
       <html>
           <h2>Corpora</h2>
           <xsl:apply-templates mode="corpus"/>
           <h2>Journals</h2>
           <xsl:apply-templates mode="journal"/>
           <h2>Monographs</h2>
        <xsl:apply-templates mode="monograph"/>
       </html>
    </xsl:template>
    
     <xsl:template match="t:bibl[@type='c']" mode="corpus">
         <p><a href="{concat('my-url',@xml:id)}"><xsl:apply-templates mode="#current"/></a> <span style="color:grey"><xsl:value-of select="@xml:id"/></span></p>
    </xsl:template>
    
    <xsl:template match="t:bibl[@type='j']" mode="journal">
        <p><a href="concat('my-url',{@xml:id})"><xsl:apply-templates/></a> <span style="color:grey"><xsl:value-of select="@xml:id"/></span></p>
    </xsl:template>
    
    <xsl:template match="t:bibl[@type='m']" mode="monograph">
        <p><a href="concat('my-url',{@xml:id})"><xsl:apply-templates/></a> <span style="color:grey"><xsl:value-of select="@xml:id"/></span></p>
    </xsl:template>
    
    <xsl:template match="t:bibl[@type='v']"/>
    <xsl:template match="t:bibl[@type='a']"/>
    
    
    <xsl:template match="t:title" mode="#all">
        <i><xsl:value-of select="."/></i>.
    </xsl:template>
    
    <xsl:template match="t:abbr[@type='primary']" mode="corpus journal">
        <xsl:value-of select="concat('[',.,'] ')"/>
    </xsl:template>
    
    <xsl:template match="t:title" mode="#all">
        <i><xsl:value-of select="."/></i>.
    </xsl:template>
    
    <xsl:template match="t:date" mode="#all">
        <xsl:value-of select="."/>
    </xsl:template>
    
    <xsl:template match="*" mode="#all"/>
   
</xsl:stylesheet>