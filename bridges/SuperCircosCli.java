import biocjava.bioDoer.JIGplotToolkit.Circos.SuperCircos.JIGSuperCircos;
import biocjava.bioDoer.JIGplotToolkit.Circos.SuperCircos.JIGSuperCircosControl;
import biocjava.bioDoer.JIGplotToolkit.Circos.SuperCircos.JIGSuperTrack;
import biocjava.bioDoer.JIGplotToolkit.Circos.LinkObj;
import biocjava.bioDoer.JIGplotToolkit.Circos.chrFeature;
import jigplot.engine.JIGBasePanel;
import jigplot.engine.JIGSubPanel;
import jigplot.engine.JIGConstants;

import java.awt.Color;
import java.awt.Font;
import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;

/**
 * SuperCircos CLI — 多轨道环形图
 * 
 * 用法:
 *   java -cp JAR:tbplot SuperCircosCli <config.cfg> <outFile> [width] [height]
 * 
 * 配置格式（行导向，# 注释）:
 *   [chrLen] <file>                    # 染色体长度文件: ChrName\tStart-End 或 ChrName\tLength
 *   [link] <file>                      # 连接文件: ChrA\tStartA\tEndA\tChrB\tStartB\tEndB\t[Color]
 *   [gene] <file>                      # 基因位置文件: Chr\tGeneName\tStart\tEnd
 *   [track] <type> <file> <startPos> <endPos> <color1> <color2> <color3> <binSize> [fillColor] [drawColor]
 *     type: Tile|Triangle|HeatMap|Point|Line|Bar|Arrow
 *     color: RGB 格式 "255,0,0" 或 颜色名 RED|ORANGE|BLUE|YELLOW|CYAN|GREEN|BLACK|WHITE|GRAY|DARK_GRAY|LIGHT_GRAY
 *   [width] <int>                      # 画布宽度 (默认 800)
 *   [height] <int>                     # 画布高度 (默认 800)
 *   [linkColor] <r,g,b>               # 连线颜色
 *   [linkStroke] <float>              # 连线粗细 (默认 1.0)
 *   [chrFillColor] <r,g,b>            # 染色体填充色
 *   [chrLabelColor] <r,g,b>           # 染色体标签色
 *   [chrLabelFont] <name> <style> <size>  # 染色体标签字体
 *   [geneLabelShow] true|false        # 是否显示基因标签
 *   [chrLabelShow] true|false         # 是否显示染色体标签
 *   [chrBarShow] true|false           # 是否显示染色体条
 *   [tickShow] true|false             # 是否显示刻度
 *   [majorTickInterval] <int>         # 主刻度间隔 (bp)
 *   [minorTickInterval] <int>         # 次刻度间隔 (bp)
 *   [startAngle] <int>                # 起始角度
 *   [endAngle] <int>                  # 结束角度
 *   [circlize] true|false             # 是否环形
 */
public class SuperCircosCli {
    
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("用法: SuperCircosCli <config.cfg> <outFile> [width] [height]");
            System.exit(1);
        }
        
        String configFile = args[0];
        String outFile = args[1];
        int width = 800;
        int height = 800;
        if (args.length > 2) width = Integer.parseInt(args[2]);
        if (args.length > 3) height = Integer.parseInt(args[3]);
        
        // 解析配置
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(configFile));
        String line;
        
        File chrLenFile = null;
        File linkFile = null;
        File geneFile = null;
        ArrayList<JIGSuperTrack> tracks = new ArrayList<JIGSuperTrack>();
        
        Color linkColor = Color.LIGHT_GRAY;
        float linkStroke = 1.0f;
        Color chrFillColor = new Color(240, 240, 240);
        Color chrLabelColor = Color.ORANGE;
        Font chrLabelFont = new Font("Arial", Font.BOLD, 14);
        boolean geneLabelShow = true;
        boolean chrLabelShow = true;
        boolean chrBarShow = true;
        boolean tickShow = true;
        int majorTickInterval = 10000000;
        int minorTickInterval = 2000000;
        int startAngle = 0;
        int endAngle = 360;
        boolean circlize = true;
        
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.startsWith("#") || line.isEmpty()) continue;
            
            String[] parts = line.split("\\s+", 2);
            String key = parts[0];
            String value = parts.length > 1 ? parts[1].trim() : "";
            
            if (key.equals("[chrLen]")) {
                chrLenFile = new File(value);
            } else if (key.equals("[link]")) {
                linkFile = new File(value);
            } else if (key.equals("[gene]")) {
                geneFile = new File(value);
            } else if (key.equals("[track]")) {
                // [track] <type> <file> <startPos> <endPos> <color1> <color2> <color3> <binSize> [fillColor] [drawColor]
                String[] tParts = value.split("\\s+");
                String trackType = tParts[0];
                File trackFile = new File(tParts[1]);
                int startPos = Integer.parseInt(tParts[2]);
                int endPos = Integer.parseInt(tParts[3]);
                Color c1 = parseColor(tParts[4]);
                Color c2 = parseColor(tParts[5]);
                Color c3 = parseColor(tParts[6]);
                int binSize = Integer.parseInt(tParts[7]);
                
                JIGSuperTrack track = new JIGSuperTrack();
                track.setInTabFile(trackFile);
                track.setInTrackType(parseTrackType(trackType));
                track.setTrackStartPos(startPos);
                track.setTrackEndPos(endPos);
                track.setEleMentColorOne(c1);
                track.setEleMentColorTwo(c2);
                track.setEleMentColorThree(c3);
                track.setBinSize(binSize);
                
                if (tParts.length > 8 && !tParts[8].equals("-")) {
                    track.setFillColor(parseColor(tParts[8]));
                }
                if (tParts.length > 9 && !tParts[9].equals("-")) {
                    track.setDrawColor(parseColor(tParts[9]));
                }
                tracks.add(track);
            } else if (key.equals("[width]")) {
                width = Integer.parseInt(value);
            } else if (key.equals("[height]")) {
                height = Integer.parseInt(value);
            } else if (key.equals("[linkColor]")) {
                linkColor = parseColor(value);
            } else if (key.equals("[linkStroke]")) {
                linkStroke = Float.parseFloat(value);
            } else if (key.equals("[chrFillColor]")) {
                chrFillColor = parseColor(value);
            } else if (key.equals("[chrLabelColor]")) {
                chrLabelColor = parseColor(value);
            } else if (key.equals("[chrLabelFont]")) {
                String[] fp = value.split("\\s+");
                String fname = fp[0];
                int fstyle = Integer.parseInt(fp[1]);
                int fsize = Integer.parseInt(fp[2]);
                chrLabelFont = new Font(fname, fstyle, fsize);
            } else if (key.equals("[geneLabelShow]")) {
                geneLabelShow = Boolean.parseBoolean(value);
            } else if (key.equals("[chrLabelShow]")) {
                chrLabelShow = Boolean.parseBoolean(value);
            } else if (key.equals("[chrBarShow]")) {
                chrBarShow = Boolean.parseBoolean(value);
            } else if (key.equals("[tickShow]")) {
                tickShow = Boolean.parseBoolean(value);
            } else if (key.equals("[majorTickInterval]")) {
                majorTickInterval = Integer.parseInt(value);
            } else if (key.equals("[minorTickInterval]")) {
                minorTickInterval = Integer.parseInt(value);
            } else if (key.equals("[startAngle]")) {
                startAngle = Integer.parseInt(value);
            } else if (key.equals("[endAngle]")) {
                endAngle = Integer.parseInt(value);
            } else if (key.equals("[circlize]")) {
                circlize = Boolean.parseBoolean(value);
            }
        }
        br.close();
        
        // 构建 SuperCircos
        JIGSuperCircos jsc = new JIGSuperCircos();
        
        // 读取 chrLen
        if (chrLenFile != null) {
            LinkedHashMap<String, long[]> chrLenMap = new LinkedHashMap<String, long[]>();
            java.io.BufferedReader chrBr = new java.io.BufferedReader(new java.io.FileReader(chrLenFile));
            String chrLine;
            while ((chrLine = chrBr.readLine()) != null) {
                if (chrLine.startsWith("#") || chrLine.trim().isEmpty()) continue;
                String[] cols = chrLine.split("\t");
                String[] rangeArr = cols[1].split("[-:]");
                if (rangeArr.length < 2) {
                    chrLenMap.put(cols[0], new long[]{0, Long.parseLong(cols[1])});
                } else {
                    chrLenMap.put(cols[0], new long[]{Long.parseLong(rangeArr[0]), Long.parseLong(rangeArr[1])});
                }
            }
            chrBr.close();
            jsc.setChrLen(chrLenMap);
        }
        
        // 读取 link
        if (linkFile != null) {
            ArrayList<LinkObj> linkArr = new ArrayList<LinkObj>();
            java.io.BufferedReader linkBr = new java.io.BufferedReader(new java.io.FileReader(linkFile));
            String linkLine;
            while ((linkLine = linkBr.readLine()) != null) {
                if (linkLine.startsWith("#") || linkLine.trim().isEmpty()) continue;
                String[] cols = linkLine.split("\t");
                if (cols.length <= 5) continue;
                LinkObj curLink = new LinkObj();
                chrFeature fromFeature = new chrFeature();
                fromFeature.chrName = cols[0];
                fromFeature.startPos = Integer.parseInt(cols[1]);
                fromFeature.endPos = Integer.parseInt(cols[2]);
                chrFeature toFeature = new chrFeature();
                toFeature.chrName = cols[3];
                toFeature.startPos = Integer.parseInt(cols[4]);
                toFeature.endPos = Integer.parseInt(cols[5]);
                curLink.fromFeature = fromFeature;
                curLink.toFeature = toFeature;
                if (cols.length > 6) {
                    curLink.color = parseColor(cols[6]);
                } else {
                    curLink.color = new Color(240, 240, 240);
                }
                linkArr.add(curLink);
            }
            linkBr.close();
            jsc.setLinkedRegion(linkArr);
        }
        
        // 读取 gene
        if (geneFile != null) {
            LinkedHashMap<String, ArrayList<chrFeature>> genePosMap = new LinkedHashMap<String, ArrayList<chrFeature>>();
            java.io.BufferedReader geneBr = new java.io.BufferedReader(new java.io.FileReader(geneFile));
            String geneLine;
            while ((geneLine = geneBr.readLine()) != null) {
                if (geneLine.startsWith("#") || geneLine.trim().isEmpty()) continue;
                String[] cols = geneLine.split("\t");
                if (cols.length <= 3) continue;
                chrFeature gf = new chrFeature();
                gf.chrName = cols[0];
                gf.featureName = cols[1];
                gf.startPos = Integer.parseInt(cols[2]);
                gf.endPos = Integer.parseInt(cols[3]);
                if (genePosMap.containsKey(gf.chrName)) {
                    genePosMap.get(gf.chrName).add(gf);
                } else {
                    ArrayList<chrFeature> arr = new ArrayList<chrFeature>();
                    arr.add(gf);
                    genePosMap.put(gf.chrName, arr);
                }
            }
            geneBr.close();
            jsc.setGenePos(genePosMap);
        }
        
        // 设置 track
        if (!tracks.isEmpty()) {
            jsc.setTrackArr(tracks);
        }
        
        // 设置参数
        jsc.setGraphWidth(width);
        jsc.setGraphHeight(height);
        jsc.setLinkColor(linkColor);
        jsc.setLinkStrokeSize(linkStroke);
        jsc.setChrFillColor(chrFillColor);
        jsc.setChrLabelColor(chrLabelColor);
        jsc.setChrLabelFont(chrLabelFont);
        jsc.setShowGeneLabel(geneLabelShow);
        jsc.setShowChrLabel(chrLabelShow);
        jsc.setShowChrBar(chrBarShow);
        jsc.setShowIntervalTick(tickShow);
        jsc.setMajorTickInterval(majorTickInterval);
        jsc.setMinorTickInterval(minorTickInterval);
        jsc.setStartAngle(startAngle);
        jsc.setEndAngle(endAngle);
        jsc.setCirclize(circlize);
        
        // 调用 plot 获取 JIGSubPanel[]
        JIGSubPanel[] subPanels = jsc.plot();
        
        // 构建 JIGBasePanel 并保存
        JIGBasePanel basePanel = new JIGBasePanel(width, height);
        for (JIGSubPanel sp : subPanels) {
            basePanel.addSubPanel(sp);
        }
        
        // 保存
        if (outFile.toLowerCase().endsWith(".svg")) {
            basePanel.save2SVG(new java.io.File(outFile));
        } else if (outFile.toLowerCase().endsWith(".png")) {
            basePanel.save2PNG(new java.io.File(outFile));
        } else if (outFile.toLowerCase().endsWith(".pdf")) {
            basePanel.save2PDF(new java.io.File(outFile));
        } else {
            basePanel.save2SVG(new java.io.File(outFile + ".svg"));
        }
        
        System.err.println("SuperCircos saved: " + outFile);
    }
    
    static Color parseColor(String s) {
        s = s.trim();
        if (s.contains(",")) {
            String[] rgb = s.split(",");
            return new Color(Integer.parseInt(rgb[0].trim()), Integer.parseInt(rgb[1].trim()), Integer.parseInt(rgb[2].trim()));
        }
        switch (s.toUpperCase()) {
            case "RED": return Color.RED;
            case "ORANGE": return Color.ORANGE;
            case "BLUE": return Color.BLUE;
            case "YELLOW": return Color.YELLOW;
            case "CYAN": return Color.CYAN;
            case "GREEN": return Color.GREEN;
            case "BLACK": return Color.BLACK;
            case "WHITE": return Color.WHITE;
            case "GRAY": return Color.GRAY;
            case "DARK_GRAY": return Color.DARK_GRAY;
            case "LIGHT_GRAY": return Color.LIGHT_GRAY;
            case "PINK": return Color.PINK;
            case "MAGENTA": return Color.MAGENTA;
            default:
                try { return Color.decode(s); } catch (Exception e) { return Color.RED; }
        }
    }
    
    static JIGSuperTrack.TrackType parseTrackType(String s) {
        switch (s.trim().toUpperCase()) {
            case "TILE": return JIGSuperTrack.TrackType.Tile;
            case "TRIANGLE": return JIGSuperTrack.TrackType.Triangle;
            case "HEATMAP": return JIGSuperTrack.TrackType.HeatMap;
            case "POINT": return JIGSuperTrack.TrackType.Point;
            case "LINE": return JIGSuperTrack.TrackType.Line;
            case "BAR": return JIGSuperTrack.TrackType.Bar;
            case "ARROW": return JIGSuperTrack.TrackType.Arrow;
            default: return JIGSuperTrack.TrackType.HeatMap;
        }
    }
}
